"""
Tests for routing logic.
"""

import pytest

from decomposition_pipeline.agents.routing import (
    select_pool_for_subproblem,
    score_domain_match,
    should_use_general_pool,
    get_routing_explanation,
    batch_route_subproblems,
    recommend_pool_scaling,
)
from decomposition_pipeline.agents.agent_types import (
    AgentPool,
    AgentPoolConfig,
    PoolType,
    PARADIGM_POOL_CONFIGS,
    DOMAIN_POOL_CONFIGS,
)


@pytest.fixture
def all_pools():
    """Create all standard pools for testing."""
    pools = {}

    # Add paradigm pools
    for name, config in PARADIGM_POOL_CONFIGS.items():
        pools[name] = AgentPool(config=config)

    # Add domain pools
    for name, config in DOMAIN_POOL_CONFIGS.items():
        pools[name] = AgentPool(config=config)

    # Add general pool
    from decomposition_pipeline.agents.agent_types import GENERAL_POOL_CONFIG
    pools["general"] = AgentPool(config=GENERAL_POOL_CONFIG)

    return pools


class TestSelectPoolForSubproblem:
    """Tests for pool selection logic."""

    def test_selects_paradigm_pool_when_specified(self, all_pools):
        """Test paradigm pool selected when source_paradigm specified."""
        subproblem = {
            "id": "sp-001",
            "title": "Test subproblem",
            "source_paradigm": "structural"
        }

        pool_name = select_pool_for_subproblem(subproblem, all_pools)
        assert pool_name == "structural"

    def test_selects_explicit_domain_when_specified(self, all_pools):
        """Test explicit domain pool selected."""
        subproblem = {
            "id": "sp-001",
            "title": "Test subproblem",
            "domain": "api_design"
        }

        pool_name = select_pool_for_subproblem(subproblem, all_pools)
        assert pool_name == "api_design"

    def test_paradigm_takes_precedence_over_domain(self, all_pools):
        """Test paradigm pool takes precedence over domain."""
        subproblem = {
            "id": "sp-001",
            "title": "Test subproblem",
            "source_paradigm": "functional",
            "domain": "api_design"
        }

        pool_name = select_pool_for_subproblem(subproblem, all_pools)
        assert pool_name == "functional"

    def test_selects_domain_by_keyword_matching(self, all_pools):
        """Test domain selected by keyword matching."""
        subproblem = {
            "id": "sp-001",
            "title": "Design REST API endpoints",
            "description": "Create RESTful API with HTTP routes and JSON responses"
        }

        pool_name = select_pool_for_subproblem(subproblem, all_pools)
        assert pool_name == "api_design"

    def test_selects_general_pool_for_ambiguous_subproblem(self, all_pools):
        """Test general pool selected when no clear match."""
        subproblem = {
            "id": "sp-001",
            "title": "Solve complex problem",
            "description": "This is a novel and complex problem"
        }

        pool_name = select_pool_for_subproblem(subproblem, all_pools)
        assert pool_name == "general"

    def test_handles_missing_pools_gracefully(self, all_pools):
        """Test handles missing pool references."""
        # Remove a pool
        del all_pools["structural"]

        subproblem = {
            "id": "sp-001",
            "title": "Test",
            "source_paradigm": "structural"  # Pool doesn't exist
        }

        # Should fall back to domain or general
        pool_name = select_pool_for_subproblem(subproblem, all_pools)
        assert pool_name in all_pools


class TestScoreDomainMatch:
    """Tests for domain matching scoring."""

    def test_api_design_keywords(self):
        """Test API design domain matching."""
        subproblem = {
            "id": "sp-001",
            "title": "API Design",
            "description": "Design REST API with endpoints and routes"
        }

        score = score_domain_match(subproblem, "api_design")
        assert score > 0.1  # Should have some matches

    def test_data_processing_keywords(self):
        """Test data processing domain matching."""
        subproblem = {
            "id": "sp-001",
            "title": "Data Pipeline",
            "description": "Build ETL pipeline for data processing and transformation"
        }

        score = score_domain_match(subproblem, "data_processing")
        assert score > 0.1

    def test_ml_modeling_keywords(self):
        """Test ML modeling domain matching."""
        subproblem = {
            "id": "sp-001",
            "title": "Train Model",
            "description": "Train machine learning model for classification"
        }

        score = score_domain_match(subproblem, "ml_modeling")
        assert score > 0.1

    def test_security_keywords(self):
        """Test security domain matching."""
        subproblem = {
            "id": "sp-001",
            "title": "Authentication",
            "description": "Implement authentication with JWT tokens and OAuth"
        }

        score = score_domain_match(subproblem, "security")
        assert score > 0.1

    def test_no_match_returns_zero(self):
        """Test no match returns low score."""
        subproblem = {
            "id": "sp-001",
            "title": "Something else",
            "description": "No relevant keywords here"
        }

        score = score_domain_match(subproblem, "api_design")
        assert score == 0.0

    def test_multiple_keywords_boost_score(self):
        """Test multiple keyword matches boost score."""
        # Few keywords
        subproblem1 = {
            "id": "sp-001",
            "title": "API endpoint",
            "description": ""
        }
        score1 = score_domain_match(subproblem1, "api_design")

        # Many keywords
        subproblem2 = {
            "id": "sp-002",
            "title": "REST API",
            "description": "Design RESTful API with HTTP endpoints, routes, and GraphQL"
        }
        score2 = score_domain_match(subproblem2, "api_design")

        assert score2 > score1

    def test_case_insensitive_matching(self):
        """Test keyword matching is case insensitive."""
        subproblem = {
            "id": "sp-001",
            "title": "REST API",
            "description": "Build REST api with ENDPOINTS"
        }

        score = score_domain_match(subproblem, "api_design")
        assert score > 0.0

    def test_word_boundary_matching(self):
        """Test uses word boundaries for matching."""
        # "api" should match in "api design" but not in "rapid"
        subproblem1 = {
            "id": "sp-001",
            "title": "API design",
            "description": ""
        }
        score1 = score_domain_match(subproblem1, "api_design")

        subproblem2 = {
            "id": "sp-002",
            "title": "Rapid development",
            "description": ""
        }
        score2 = score_domain_match(subproblem2, "api_design")

        assert score1 > score2


class TestShouldUseGeneralPool:
    """Tests for general pool decision logic."""

    def test_uses_general_when_no_strong_matches(self):
        """Test uses general pool when no strong domain matches."""
        subproblem = {
            "id": "sp-001",
            "title": "Generic problem",
            "description": "No specific domain"
        }
        domain_scores = {"api_design": 0.2, "data_processing": 0.1}

        assert should_use_general_pool(subproblem, domain_scores) is True

    def test_not_general_when_strong_match(self):
        """Test doesn't use general pool when strong domain match."""
        subproblem = {
            "id": "sp-001",
            "title": "API problem",
            "description": ""
        }
        domain_scores = {"api_design": 0.8, "data_processing": 0.1}

        assert should_use_general_pool(subproblem, domain_scores) is False

    def test_not_general_when_paradigm_specified(self):
        """Test doesn't use general when paradigm specified."""
        subproblem = {
            "id": "sp-001",
            "title": "Problem",
            "source_paradigm": "structural"
        }
        domain_scores = {}

        assert should_use_general_pool(subproblem, domain_scores) is False

    def test_uses_general_for_complex_problems(self):
        """Test uses general pool for complex/novel problems."""
        subproblem = {
            "id": "sp-001",
            "title": "Novel complex problem",
            "description": "This is an experimental research prototype"
        }
        domain_scores = {}

        assert should_use_general_pool(subproblem, domain_scores) is True


class TestGetRoutingExplanation:
    """Tests for routing explanation generation."""

    def test_explanation_includes_paradigm(self, all_pools):
        """Test explanation includes paradigm routing."""
        subproblem = {
            "id": "sp-001",
            "title": "Test",
            "source_paradigm": "functional"
        }

        explanation = get_routing_explanation(subproblem, "functional", all_pools)

        assert explanation["selected_pool"] == "functional"
        assert any(
            r["strategy"] == "paradigm" for r in explanation["reasoning"]
        )

    def test_explanation_includes_domain_scores(self, all_pools):
        """Test explanation includes domain scores."""
        subproblem = {
            "id": "sp-001",
            "title": "API design",
            "description": "REST API endpoints"
        }

        explanation = get_routing_explanation(subproblem, "api_design", all_pools)

        assert "domain_scores" in explanation
        assert "api_design" in explanation["domain_scores"]

    def test_explanation_includes_general_fallback(self, all_pools):
        """Test explanation includes general fallback reason."""
        subproblem = {
            "id": "sp-001",
            "title": "Generic problem",
            "description": ""
        }

        explanation = get_routing_explanation(subproblem, "general", all_pools)

        assert any(
            r["strategy"] == "general_fallback" for r in explanation["reasoning"]
        )


class TestBatchRouteSubproblems:
    """Tests for batch routing."""

    def test_batch_routes_multiple_subproblems(self, all_pools):
        """Test batch routing distributes subproblems."""
        subproblems = [
            {"id": "sp-001", "title": "REST API endpoints", "description": "Create REST API with HTTP routes"},
            {"id": "sp-002", "title": "Data pipeline ETL", "description": "Build data processing pipeline"},
            {"id": "sp-003", "title": "Security authentication", "description": "Implement authentication with JWT"},
            {"id": "sp-004", "title": "Generic", "description": "Something else"},
        ]

        routing = batch_route_subproblems(subproblems, all_pools)

        assert "api_design" in routing
        assert "data_processing" in routing
        assert "security" in routing
        assert "general" in routing

        # Check assignments - at least one should match each domain
        assert len(routing["api_design"]) > 0 or len(routing["data_processing"]) > 0 or len(routing["security"]) > 0

    def test_batch_routing_with_paradigms(self, all_pools):
        """Test batch routing respects paradigm assignments."""
        subproblems = [
            {"id": "sp-001", "source_paradigm": "structural"},
            {"id": "sp-002", "source_paradigm": "functional"},
            {"id": "sp-003", "source_paradigm": "temporal"},
        ]

        routing = batch_route_subproblems(subproblems, all_pools)

        assert "sp-001" in routing["structural"]
        assert "sp-002" in routing["functional"]
        assert "sp-003" in routing["temporal"]


class TestRecommendPoolScaling:
    """Tests for pool scaling recommendations."""

    def test_recommends_scale_up_for_high_utilization(self, all_pools):
        """Test recommends scaling up when utilization high."""
        routing = {
            "api_design": ["sp-{:03d}".format(i) for i in range(28)],  # 28/30 = 93%
            "general": [],
        }

        recommendations = recommend_pool_scaling(routing, all_pools)

        assert recommendations["api_design"]["action"] == "scale_up"
        assert recommendations["api_design"]["suggested_size"] > 30

    def test_recommends_scale_down_for_low_utilization(self, all_pools):
        """Test recommends scaling down when utilization low."""
        routing = {
            "structural": ["sp-001", "sp-002"],  # 2/50 = 4%
            "general": [],
        }

        recommendations = recommend_pool_scaling(routing, all_pools)

        assert recommendations["structural"]["action"] == "scale_down"
        assert recommendations["structural"]["suggested_size"] < 50

    def test_no_action_for_balanced_utilization(self, all_pools):
        """Test no action when utilization balanced."""
        routing = {
            "functional": ["sp-{:03d}".format(i) for i in range(25)],  # 25/50 = 50%
            "general": [],
        }

        recommendations = recommend_pool_scaling(routing, all_pools)

        assert recommendations["functional"]["action"] == "none"

    def test_includes_utilization_metrics(self, all_pools):
        """Test recommendations include utilization metrics."""
        routing = {
            "data": ["sp-001"],
            "general": [],
        }

        recommendations = recommend_pool_scaling(routing, all_pools)

        assert "utilization" in recommendations["data"]
        assert "expected_load" in recommendations["data"]
        assert "current_capacity" in recommendations["data"]
