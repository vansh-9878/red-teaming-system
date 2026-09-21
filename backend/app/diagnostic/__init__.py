"""
Module 5: Diagnostic Module for SentinelLoop.
Analyzes successful rounds to identify attack categories, failure layers (input vs prompt),
and generates structured diagnosis objects for Module 6 (Patch Generator).
"""
from app.diagnostic.engine import DiagnosticEngine

diagnostic_engine = DiagnosticEngine()

__all__ = ["DiagnosticEngine", "diagnostic_engine"]
