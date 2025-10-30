"""
Core data models for the Technique Catalog.

These models define the structure for storing and retrieving algorithmic
decomposition techniques from computer science literature.
"""

from typing import Any

from pydantic import BaseModel, Field


class ApplicabilityRule(BaseModel):
    """
    A rule that determines when a technique is applicable to a problem.

    Rules are evaluated against problem characteristics and return a score
    indicating how well the technique fits the problem.
    """

    condition: str = Field(
        ...,
        description="Condition to check (e.g., 'problem_size > 1000')",
        examples=["problem_size > 1000", "has_recursive_structure == true"],
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score to assign if condition is met (0.0-1.0)",
    )
    description: str = Field(
        ...,
        description="Human-readable explanation of why this rule matters",
        examples=["Large problems benefit from divide-and-conquer approach"],
    )

    def evaluate(self, characteristics: dict[str, Any]) -> tuple[bool, float]:
        """
        Evaluate this rule against problem characteristics.

        Args:
            characteristics: Dict of problem characteristics

        Returns:
            Tuple of (condition_met, score)
        """
        try:
            # Simple evaluation of condition
            # In production, you'd want a safer expression evaluator
            result = eval(self.condition, {"__builtins__": {}}, characteristics)
            return (bool(result), self.score if result else 0.0)
        except Exception:
            # If evaluation fails, condition is not met
            return (False, 0.0)


class Technique(BaseModel):
    """
    An algorithmic decomposition technique from computer science literature.

    Each technique represents a well-established method for breaking down
    problems, with formal definitions and applicability criteria.
    """

    name: str = Field(
        ...,
        description="Name of the technique",
        examples=["Divide and Conquer", "MapReduce", "Event Sourcing"],
    )
    paradigm: str = Field(
        ...,
        description="Decomposition paradigm this technique belongs to",
        examples=[
            "structural",
            "functional",
            "temporal",
            "spatial",
            "hierarchical",
            "computational",
            "data",
            "dependency",
        ],
    )
    formal_definition: str = Field(
        ...,
        description="Mathematical or algorithmic definition of the technique",
        examples=["T(n) = aT(n/b) + f(n)", "map: (k1,v1) → [(k2,v2)], reduce: (k2,[v2]) → [v3]"],
    )
    prerequisites: list[str] = Field(
        default_factory=list,
        description="Requirements that must be met for this technique to apply",
        examples=[["problem_is_divisible", "subproblems_independent"]],
    )
    complexity: str = Field(
        ...,
        description="Time/space complexity characteristics",
        examples=["O(n log n) typical", "O(n/p) with p processors"],
    )
    applicability_rules: list[ApplicabilityRule] = Field(
        default_factory=list,
        description="Rules for scoring technique applicability",
    )
    literature_references: list[str] = Field(
        default_factory=list,
        description="Citations to papers, textbooks, or other sources",
        examples=[["CLRS Ch 4", "Bentley 1980"]],
    )
    implementation_strategy: str = Field(
        ...,
        description="High-level strategy for how agents should apply this technique",
        examples=["Recursively split, solve subproblems, merge results"],
    )

    def check_prerequisites(self, characteristics: dict[str, Any]) -> bool:
        """
        Check if all prerequisites are satisfied by the problem characteristics.

        Args:
            characteristics: Dict of problem characteristics

        Returns:
            True if all prerequisites are met, False otherwise
        """
        for prereq in self.prerequisites:
            if not characteristics.get(prereq, False):
                return False
        return True

    def score_applicability(self, characteristics: dict[str, Any]) -> float:
        """
        Score how applicable this technique is to a problem.

        Args:
            characteristics: Dict of problem characteristics

        Returns:
            Applicability score from 0.0 to 1.0
        """
        if not self.applicability_rules:
            return 0.5  # Default score if no rules defined

        total_score = 0.0
        total_weight = 0.0

        for rule in self.applicability_rules:
            met, score = rule.evaluate(characteristics)
            if met:
                total_score += score
                total_weight += 1.0

        return total_score / total_weight if total_weight > 0 else 0.0


class TechniqueCatalog(BaseModel):
    """
    Catalog of pre-defined algorithmic decomposition techniques.

    The catalog is organized by paradigm and provides methods for retrieving
    and scoring techniques based on problem characteristics.
    """

    techniques: dict[str, list[Technique]] = Field(
        default_factory=dict,
        description="Techniques organized by paradigm",
    )
    version: str = Field(
        default="1.0.0",
        description="Catalog version for tracking updates",
    )

    def add_technique(self, technique: Technique) -> None:
        """Add a technique to the catalog."""
        if technique.paradigm not in self.techniques:
            self.techniques[technique.paradigm] = []
        self.techniques[technique.paradigm].append(technique)

    def get_paradigms(self) -> list[str]:
        """Get list of all paradigms in the catalog."""
        return list(self.techniques.keys())

    def get_techniques_for_paradigm(self, paradigm: str) -> list[Technique]:
        """Get all techniques for a specific paradigm."""
        return self.techniques.get(paradigm, [])

    def get_applicable_techniques(
        self,
        paradigm: str,
        problem_characteristics: dict[str, Any],
    ) -> list[tuple[Technique, float]]:
        """
        Get techniques applicable to a problem, sorted by score.

        Args:
            paradigm: Decomposition paradigm to search within
            problem_characteristics: Dict of problem characteristics

        Returns:
            List of (technique, score) tuples, sorted by score descending
        """
        candidates = self.techniques.get(paradigm, [])

        # Filter by prerequisites and score
        scored_techniques = []
        for technique in candidates:
            if technique.check_prerequisites(problem_characteristics):
                score = technique.score_applicability(problem_characteristics)
                if score > 0:
                    scored_techniques.append((technique, score))

        # Sort by score descending
        scored_techniques.sort(key=lambda x: x[1], reverse=True)
        return scored_techniques

    def get_best_technique(
        self,
        paradigm: str,
        problem_characteristics: dict[str, Any],
    ) -> tuple[Technique, float] | None:
        """
        Get the best technique for a paradigm and problem.

        Args:
            paradigm: Decomposition paradigm
            problem_characteristics: Dict of problem characteristics

        Returns:
            (technique, score) tuple or None if no applicable techniques
        """
        applicable = self.get_applicable_techniques(paradigm, problem_characteristics)
        return applicable[0] if applicable else None

    def to_dict(self) -> dict[str, Any]:
        """Export catalog to dictionary for serialization."""
        return {
            "version": self.version,
            "techniques": {
                paradigm: [tech.model_dump() for tech in techniques]
                for paradigm, techniques in self.techniques.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TechniqueCatalog":
        """Load catalog from dictionary."""
        techniques_dict = {}
        for paradigm, tech_list in data.get("techniques", {}).items():
            techniques_dict[paradigm] = [Technique(**tech) for tech in tech_list]

        return cls(
            version=data.get("version", "1.0.0"),
            techniques=techniques_dict,
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the catalog."""
        total_techniques = sum(len(techs) for techs in self.techniques.values())
        return {
            "version": self.version,
            "total_paradigms": len(self.techniques),
            "total_techniques": total_techniques,
            "techniques_per_paradigm": {
                paradigm: len(techs) for paradigm, techs in self.techniques.items()
            },
        }
