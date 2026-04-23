"""
Tests for context validation workflow.
"""

import pytest
from pathlib import Path
from dbt_project.validation import (
    LLMContextValidator,
    HumanReviewQueue,
    ContextValidationOrchestrator,
    ReviewDecision,
)


@pytest.fixture
def temp_context_file(tmp_path):
    """Create a test context file."""
    content = """# Contexte - Clients

## Objectifs

Identifier and segment customers by lifecycle stage.

Grain: One row per customer unique ID.

## Source

Source table: `raw_salesforce_accounts`
- From Salesforce CRM
- Last updated daily

## Transformations

1. Deduplication by account ID (keep latest)
2. Filter active accounts only
3. Calculate lifecycle metrics

## Champs

- `customer_id` (STRING): Unique Salesforce account ID
- `customer_name` (STRING): Account name
- `lifecycle_stage` (STRING): Prospect | Customer | Churned
- `created_at` (TIMESTAMP): When account was created
- `last_activity_at` (TIMESTAMP): Last interaction

## Tests et Validations

- PRIMARY KEY: customer_id must be unique
- NOT NULL: customer_id, customer_name
- ACCEPTED_VALUES: lifecycle_stage in (Prospect, Customer, Churned)
"""
    context_file = tmp_path / "dim_customers.context.md"
    context_file.write_text(content)
    return context_file


@pytest.fixture
def incomplete_context_file(tmp_path):
    """Create an incomplete context file."""
    content = """# Context

This is incomplete.
"""
    context_file = tmp_path / "incomplete.context.md"
    context_file.write_text(content)
    return context_file


class TestLLMContextValidator:
    """Tests for LLM context validator."""

    def test_validate_complete_context(self, temp_context_file):
        """Test validation of a complete context file."""
        validator = LLMContextValidator()
        result = validator.validate_context_file(str(temp_context_file))

        assert result.is_valid
        assert result.confidence > 0.7
        assert len(result.issues) == 0

    def test_validate_incomplete_context(self, incomplete_context_file):
        """Test validation of incomplete context file."""
        validator = LLMContextValidator()
        result = validator.validate_context_file(str(incomplete_context_file))

        assert not result.is_valid
        assert result.confidence < 0.5
        assert len(result.issues) > 0

    def test_missing_objectives_section(self, tmp_path):
        """Test detection of missing objectives."""
        content = "## Source\nSome data\n"
        context_file = tmp_path / "no_objectives.context.md"
        context_file.write_text(content)

        validator = LLMContextValidator()
        result = validator.validate_context_file(str(context_file))

        assert not result.is_valid
        critical_issues = [i for i in result.issues if i.severity.value == "critical"]
        assert len(critical_issues) > 0

    def test_missing_transformations(self, tmp_path):
        """Test detection of missing transformations."""
        content = "## Objectifs\nDo something\n## Source\nFrom somewhere\n"
        context_file = tmp_path / "no_transforms.context.md"
        context_file.write_text(content)

        validator = LLMContextValidator()
        result = validator.validate_context_file(str(context_file))

        # Should have issues about missing transformations
        assert any("transformation" in i.message.lower() for i in result.issues)

    def test_file_not_found(self):
        """Test handling of missing file."""
        validator = LLMContextValidator()
        result = validator.validate_context_file("/nonexistent/file.md")

        assert not result.is_valid
        assert len(result.issues) > 0
        assert any("not found" in i.message.lower() for i in result.issues)


class TestHumanReviewQueue:
    """Tests for human review queue."""

    def test_add_item_to_queue(self, tmp_path):
        """Test adding item to review queue."""
        queue = HumanReviewQueue(storage_path=str(tmp_path))

        item = queue.add_item(
            file_path="models/dim_customers.context.md",
            model_name="dim_customers",
            llm_confidence=0.65,
            llm_issues_count=3,
        )

        assert item.model_name == "dim_customers"
        assert item.status == ReviewDecision.PENDING

    def test_queue_prioritization(self, tmp_path):
        """Test that queue items are prioritized correctly."""
        queue = HumanReviewQueue(storage_path=str(tmp_path))

        # Add low confidence item (should be high priority)
        low_conf = queue.add_item(
            file_path="low.md",
            model_name="low_confidence",
            llm_confidence=0.2,
            llm_issues_count=6,
        )

        # Add high confidence item (should be low priority)
        high_conf = queue.add_item(
            file_path="high.md",
            model_name="high_confidence",
            llm_confidence=0.95,
            llm_issues_count=0,
        )

        queued = queue.get_queue()
        assert queued[0].model_name == "low_confidence"
        assert queued[1].model_name == "high_confidence"

    def test_submit_review(self, tmp_path):
        """Test submitting a human review."""
        queue = HumanReviewQueue(storage_path=str(tmp_path))

        queue.add_item(
            file_path="models/test.context.md",
            model_name="test_model",
            llm_confidence=0.6,
            llm_issues_count=2,
        )

        success = queue.submit_review(
            model_name="test_model",
            decision=ReviewDecision.APPROVED,
            reviewer="reviewer@example.com",
            comments=[],
            approved_sections=["all"],
            rejected_sections=[],
            revision_requests=[],
        )

        assert success

    def test_queue_statistics(self, tmp_path):
        """Test queue statistics generation."""
        queue = HumanReviewQueue(storage_path=str(tmp_path))

        queue.add_item("a.md", "model_a", 0.5, 4)  # CRITICAL
        queue.add_item("b.md", "model_b", 0.7, 3)  # HIGH
        queue.add_item("c.md", "model_c", 0.9, 0)  # LOW

        stats = queue.get_statistics()

        assert stats["total_items"] == 3
        assert stats["pending"] == 3
        assert stats["by_priority"]["critical"] == 1
        assert stats["by_priority"]["high"] == 1
        assert stats["by_priority"]["low"] == 1


class TestContextValidationOrchestrator:
    """Tests for the full validation orchestrator."""

    def test_validate_context_workflow(self, temp_context_file, tmp_path):
        """Test complete validation workflow."""
        orchestrator = ContextValidationOrchestrator(
            review_queue=HumanReviewQueue(storage_path=str(tmp_path))
        )

        result = orchestrator.validate_context(
            str(temp_context_file), "dim_customers"
        )

        assert result.model_name == "dim_customers"
        assert result.llm_validation.is_valid
        assert result.is_approved  # Should pass without human review

    def test_context_requiring_review(self, incomplete_context_file, tmp_path):
        """Test workflow for context requiring human review."""
        orchestrator = ContextValidationOrchestrator(
            review_queue=HumanReviewQueue(storage_path=str(tmp_path))
        )

        result = orchestrator.validate_context(
            str(incomplete_context_file), "bad_context"
        )

        assert result.human_review_required
        assert result.final_status == ReviewDecision.PENDING

    def test_validate_all_contexts(self, tmp_path):
        """Test validating all contexts in a directory."""
        # Create test models directory
        models_dir = tmp_path / "models"
        models_dir.mkdir()

        # Create context files
        (models_dir / "dim_a.context.md").write_text("## Objectifs\nTest\n## Champs\nField")
        (models_dir / "dim_b.context.md").write_text("## Objectifs\nTest\n## Champs\nField")

        orchestrator = ContextValidationOrchestrator(
            review_queue=HumanReviewQueue(storage_path=str(tmp_path))
        )

        results = orchestrator.validate_all_contexts(str(models_dir))

        assert len(results) == 2

    def test_approve_context(self, tmp_path):
        """Test approving a context."""
        orchestrator = ContextValidationOrchestrator(
            review_queue=HumanReviewQueue(storage_path=str(tmp_path))
        )

        # Add to queue first
        orchestrator.review_queue.add_item(
            "test.md", "test_model", 0.7, 1
        )

        # Then approve
        success = orchestrator.approve_context(
            "test_model",
            "reviewer@example.com",
            "Looks good!",
        )

        assert success

    def test_get_validation_report(self, tmp_path):
        """Test generating validation report."""
        orchestrator = ContextValidationOrchestrator(
            review_queue=HumanReviewQueue(storage_path=str(tmp_path))
        )

        orchestrator.review_queue.add_item("a.md", "model_a", 0.5, 4)
        orchestrator.review_queue.add_item("b.md", "model_b", 0.7, 2)

        report = orchestrator.get_validation_report()

        assert report["summary"]["total_contexts_queued"] == 2
        assert report["summary"]["pending_review"] == 2
        assert "by_priority" in report
