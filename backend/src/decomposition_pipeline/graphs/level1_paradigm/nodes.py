"""
Node implementations for Level 1 Paradigm Selection Subgraph.

Contains the three main nodes:
1. characterize_problem - Extracts problem characteristics
2. score_paradigms - Scores each paradigm for applicability
3. select_paradigms - Selects top paradigms based on scores
"""

import json
import logging
from typing import Any

from openai import OpenAI

from decomposition_pipeline.config.settings import get_settings
from decomposition_pipeline.schemas import Level1State, ParadigmType

from .prompts import (
    get_characterization_prompt,
    get_paradigm_scoring_prompt,
)

logger = logging.getLogger(__name__)

# Initialize settings and LLM client
settings = get_settings()

# Use appropriate client based on configuration
if settings.default_llm_provider == "openai":
    client = OpenAI(api_key=settings.openai_api_key)
    model = "gpt-4o-mini"
else:
    from anthropic import Anthropic
    client = Anthropic(api_key=settings.anthropic_api_key)  # type: ignore
    model = settings.default_model


def characterize_problem(state: Level1State) -> Level1State:
    """
    Node 1: Problem Characterization.

    Extracts key characteristics from the problem description that will be used
    to score paradigm applicability.

    Args:
        state: Level1State with original_problem

    Returns:
        Updated state with problem_characteristics
    """
    logger.info("Characterizing problem...")

    problem = state["original_problem"]

    # Generate characterization prompt
    prompt = get_characterization_prompt(problem)

    try:
        # Call LLM API with JSON mode for structured output
        if settings.default_llm_provider == "openai":
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing problems and extracting their key characteristics for decomposition.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            characteristics_str = response.choices[0].message.content
        else:
            # Anthropic doesn't have native JSON mode, so we request JSON in the prompt
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                temperature=0.2,
                system="You are an expert at analyzing problems and extracting their key characteristics for decomposition. Always respond with valid JSON.",
                messages=[
                    {"role": "user", "content": prompt + "\n\nRespond with valid JSON only, no other text."},
                ],
            )
            characteristics_str = response.content[0].text  # type: ignore

        if not characteristics_str:
            raise ValueError("Empty response from LLM")

        characteristics = json.loads(characteristics_str)

        logger.info(f"Extracted characteristics: {characteristics}")

        return {
            **state,
            "problem_characteristics": characteristics,
        }

    except Exception as e:
        logger.error(f"Error in characterize_problem: {e}")
        # Return default characteristics on error
        return {
            **state,
            "problem_characteristics": {
                "problem_size": "unknown",
                "error": str(e),
            },
        }


def score_paradigms(state: Level1State) -> Level1State:
    """
    Node 2: Paradigm Scoring.

    Scores each of the 8 paradigms for how well they apply to the problem.

    Args:
        state: Level1State with original_problem and problem_characteristics

    Returns:
        Updated state with paradigm_scores and candidate_paradigms
    """
    logger.info("Scoring paradigms...")

    problem = state["original_problem"]
    characteristics = state.get("problem_characteristics", {})

    # All 8 paradigms to score
    paradigms = [p.value for p in ParadigmType]

    paradigm_scores: dict[str, float] = {}
    candidate_paradigms: list[dict[str, Any]] = []
    paradigm_reasoning: dict[str, str] = {}

    for paradigm in paradigms:
        try:
            # Generate scoring prompt for this paradigm
            prompt = get_paradigm_scoring_prompt(
                problem=problem,
                characteristics=characteristics,
                paradigm=paradigm,
            )

            # Call LLM API
            if settings.default_llm_provider == "openai":
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at evaluating decomposition paradigms for problems.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                result_str = response.choices[0].message.content
            else:
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    temperature=0.2,
                    system="You are an expert at evaluating decomposition paradigms for problems. Always respond with valid JSON.",
                    messages=[
                        {"role": "user", "content": prompt + "\n\nRespond with valid JSON only, no other text."},
                    ],
                )
                result_str = response.content[0].text  # type: ignore

            if not result_str:
                raise ValueError(f"Empty response for paradigm {paradigm}")

            result = json.loads(result_str)
            score = float(result.get("score", 0.0))
            reasoning = result.get("reasoning", "")
            key_indicators = result.get("key_indicators", [])

            paradigm_scores[paradigm] = score
            paradigm_reasoning[paradigm] = reasoning

            candidate_paradigms.append({
                "paradigm": paradigm,
                "score": score,
                "reasoning": reasoning,
                "key_indicators": key_indicators,
            })

            logger.info(f"{paradigm}: {score:.2f} - {reasoning}")

        except Exception as e:
            logger.error(f"Error scoring paradigm {paradigm}: {e}")
            paradigm_scores[paradigm] = 0.0
            paradigm_reasoning[paradigm] = f"Error: {e}"
            candidate_paradigms.append({
                "paradigm": paradigm,
                "score": 0.0,
                "reasoning": f"Error: {e}",
                "key_indicators": [],
            })

    # Sort candidates by score (descending)
    candidate_paradigms.sort(key=lambda x: x["score"], reverse=True)

    return {
        **state,
        "paradigm_scores": paradigm_scores,
        "candidate_paradigms": candidate_paradigms,
        "paradigm_reasoning": paradigm_reasoning,
    }


def select_paradigms(state: Level1State) -> Level1State:
    """
    Node 3: Paradigm Selection.

    Selects top 1-3 paradigms based on scores and threshold criteria.

    Args:
        state: Level1State with paradigm_scores

    Returns:
        Updated state with selected_paradigms
    """
    logger.info("Selecting paradigms...")

    candidate_paradigms = state.get("candidate_paradigms", [])

    # Selection criteria from brainstorm_1.md:
    # - Select top 1-3 paradigms with score > 0.6
    # - Can select multiple if problem has multiple decomposition axes

    selected_paradigms: list[str] = []
    selection_threshold = 0.6
    max_paradigms = 3

    for candidate in candidate_paradigms[:max_paradigms]:
        score = candidate["score"]
        paradigm = candidate["paradigm"]

        if score >= selection_threshold:
            selected_paradigms.append(paradigm)
            logger.info(f"Selected paradigm: {paradigm} (score: {score:.2f})")
        else:
            logger.info(f"Rejected paradigm: {paradigm} (score: {score:.2f}, below threshold)")

    if not selected_paradigms:
        logger.warning("No paradigms met the selection threshold")

    logger.info(f"Final selection: {selected_paradigms}")

    return {
        **state,
        "selected_paradigms": selected_paradigms,
    }


def request_more_context(state: Level1State) -> Level1State:
    """
    Node 4: Request More Context.

    This node is triggered when all paradigm scores are too low (< 0.3),
    indicating the problem needs more context or clarification.

    Args:
        state: Level1State with paradigm_scores

    Returns:
        Updated state with request for more context
    """
    logger.warning("All paradigm scores are low - requesting more context")

    paradigm_scores = state.get("paradigm_scores", {})
    max_score = max(paradigm_scores.values()) if paradigm_scores else 0.0

    # Add a message to the state indicating more context is needed
    return {
        **state,
        "selected_paradigms": [],
        "paradigm_reasoning": {
            **state.get("paradigm_reasoning", {}),
            "_system_message": (
                f"Unable to confidently select a paradigm (max score: {max_score:.2f}). "
                "Please provide more details about the problem, including: "
                "problem structure, scale, constraints, and decomposition goals."
            ),
        },
    }
