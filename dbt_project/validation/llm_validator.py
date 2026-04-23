"""
LLM Context Validator

Uses Claude as a judge to validate context files against a set of criteria.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue found by the LLM."""

    severity: ValidationSeverity
    category: str
    message: str
    suggestion: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of LLM validation."""

    file_path: str
    is_valid: bool
    confidence: float  # 0-1
    issues: list[ValidationIssue]
    summary: str
    metadata: dict


class LLMContextValidator:
    """
    Validates context files using LLM (Claude) as a judge.

    Context files should contain:
    - Objectives: Clear business purpose
    - Grain: Data granularity
    - Transformations: Source data and logic applied
    - Expected fields: Column definitions
    - Data quality rules: Tests and validations
    """

    # Validation criteria - can be extended
    VALIDATION_CRITERIA = {
        "has_objectives": "Must clearly define business objectives and grain",
        "has_source_info": "Must document source tables and data lineage",
        "has_transformations": "Must explain transformations applied",
        "has_field_catalog": "Must list all expected fields with types",
        "has_quality_rules": "Must define data quality tests",
        "has_exclusions": "Should document any exclusions or filters",
        "completeness": "All sections should be adequately detailed",
        "clarity": "Writing should be clear and unambiguous",
    }

    def __init__(self, llm_client=None):
        """
        Initialize validator.

        Args:
            llm_client: Optional LLM client (defaults to Claude via env)
        """
        self.llm_client = llm_client
        self._init_llm()

    def _init_llm(self):
        """Initialize LLM client (stub for now)."""
        if self.llm_client is None:
            # In production, this would initialize Anthropic client
            logger.info("LLM client not provided, using mock validation")

    def validate_context_file(self, file_path: str) -> ValidationResult:
        """
        Validate a context file.

        Args:
            file_path: Path to the context file

        Returns:
            ValidationResult with issues and overall validity
        """
        path = Path(file_path)

        if not path.exists():
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                confidence=1.0,
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category="file_not_found",
                        message=f"Context file not found: {file_path}",
                    )
                ],
                summary="File does not exist",
                metadata={},
            )

        # Read context file
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                confidence=1.0,
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category="read_error",
                        message=f"Failed to read file: {str(e)}",
                    )
                ],
                summary=f"Error reading file: {str(e)}",
                metadata={},
            )

        # Validate structure
        issues = self._validate_structure(content)

        # Determine validity
        is_valid = not any(
            issue.severity == ValidationSeverity.CRITICAL for issue in issues
        )

        # Calculate confidence (higher = better)
        critical_count = sum(
            1 for i in issues if i.severity == ValidationSeverity.CRITICAL
        )
        high_count = sum(1 for i in issues if i.severity == ValidationSeverity.HIGH)
        confidence = max(0.0, 1.0 - (critical_count * 0.3 + high_count * 0.1))

        # Create summary
        summary = self._create_summary(issues, is_valid)

        return ValidationResult(
            file_path=file_path,
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            summary=summary,
            metadata={
                "file_size": len(content),
                "has_sections": self._extract_sections(content),
            },
        )

    def _validate_structure(self, content: str) -> list[ValidationIssue]:
        """Validate file structure against criteria."""
        issues = []

        # Check for required sections
        sections = {
            "objectives": ("## Objectifs" in content or "# Objectifs" in content),
            "source": ("Source" in content or "source" in content),
            "transformations": (
                "Transformations" in content or "transformations" in content
            ),
            "fields": ("Champs" in content or "Fields" in content or "columns" in content),
            "quality": ("Tests" in content or "Quality" in content or "Validations" in content),
        }

        # Objectives are mandatory
        if not sections["objectives"]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="missing_section",
                    message="Missing 'Objectifs' section",
                    suggestion="Add a clear 'Objectifs' section describing the business purpose",
                )
            )

        # Source information is important
        if not sections["source"]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category="missing_section",
                    message="Missing source data documentation",
                    suggestion="Document where data comes from and lineage",
                )
            )

        # Transformations are important
        if not sections["transformations"]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category="missing_section",
                    message="Missing transformation documentation",
                    suggestion="Explain what transformations are applied to the data",
                )
            )

        # Fields catalog is important
        if not sections["fields"]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category="missing_section",
                    message="Missing field definitions",
                    suggestion="List all expected fields with their types and descriptions",
                )
            )

        # Quality rules are recommended
        if not sections["quality"]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.MEDIUM,
                    category="missing_section",
                    message="Missing data quality rules",
                    suggestion="Define tests and validations (uniqueness, not null, etc)",
                )
            )

        # Check length (too short = incomplete)
        if len(content) < 200:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category="insufficient_detail",
                    message="Context file appears incomplete (very short)",
                    suggestion="Provide more detailed documentation",
                )
            )

        return issues

    def _extract_sections(self, content: str) -> list[str]:
        """Extract markdown sections from content."""
        sections = []
        for line in content.split("\n"):
            if line.startswith("#"):
                sections.append(line.lstrip("#").strip())
        return sections

    def _create_summary(self, issues: list[ValidationIssue], is_valid: bool) -> str:
        """Create a human-readable summary."""
        if not issues:
            return "✅ Context file is valid and complete"

        critical = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        high = [i for i in issues if i.severity == ValidationSeverity.HIGH]
        medium = [i for i in issues if i.severity == ValidationSeverity.MEDIUM]

        parts = []
        if critical:
            parts.append(f"🔴 {len(critical)} critical issue(s)")
        if high:
            parts.append(f"🟠 {len(high)} high severity issue(s)")
        if medium:
            parts.append(f"🟡 {len(medium)} medium severity issue(s)")

        status = "❌ INVALID" if not is_valid else "⚠️ NEEDS REVIEW"
        return f"{status}: {', '.join(parts)}"

    def validate_model_context_pair(
        self, model_path: str, context_path: str
    ) -> ValidationResult:
        """
        Validate that context matches the model.

        Args:
            model_path: Path to dbt SQL model
            context_path: Path to context file

        Returns:
            Validation result comparing model and context
        """
        # For now, validate the context file
        # In production, would compare model structure with context
        return self.validate_context_file(context_path)
