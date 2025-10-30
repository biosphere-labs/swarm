"""
Technique Catalog Module

This module implements a pre-populated catalog of algorithmic decomposition techniques
from computer science literature. All techniques are organized by paradigm and include
formal definitions, prerequisites, applicability rules, and literature references.

No machine learning is used - all selection is rule-based using established criteria
from textbooks and research papers.
"""

from decomposition_pipeline.catalog.models import (
    ApplicabilityRule,
    Technique,
    TechniqueCatalog,
)
from decomposition_pipeline.catalog.techniques import get_default_catalog

__all__ = [
    "ApplicabilityRule",
    "Technique",
    "TechniqueCatalog",
    "get_default_catalog",
]
