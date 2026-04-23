"""
Context Validation Orchestrator

Orchestrates the full validation workflow:
1. LLM validation
2. Human review queue
3. Approval/rejection
4. Reporting
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .llm_validator import LLMContextValidator, ValidationResult
from .human_review import HumanReviewQueue, ReviewDecision, ReviewPriority

logger = logging.getLogger(__name__)


@dataclass
class ValidationWorkflowResult:
    """Result of the full validation workflow."""

    model_name: str
    llm_validation: ValidationResult
    human_review_required: bool
    review_priority: Optional[ReviewPriority] = None
    final_status: Optional[ReviewDecision] = None
    is_approved: bool = False


class ContextValidationOrchestrator:
    """
    Orchestrates the context validation workflow:

    1. **LLM Validation Phase**: Automatic checks for completeness and structure
    2. **Review Queue Assignment**: High-risk contexts go to human reviewers
    3. **Human Review Phase**: Domain experts validate context appropriateness
    4. **Final Approval**: Contexts approved if LLM + Human agree
    """

    def __init__(
        self,
        llm_validator: Optional[LLMContextValidator] = None,
        review_queue: Optional[HumanReviewQueue] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            llm_validator: LLM validator instance
            review_queue: Human review queue instance
        """
        self.llm_validator = llm_validator or LLMContextValidator()
        self.review_queue = review_queue or HumanReviewQueue()

    def validate_context(
        self, context_file: str, model_name: str
    ) -> ValidationWorkflowResult:
        """
        Run full validation workflow on a context file.

        Args:
            context_file: Path to context file
            model_name: Name of the dbt model

        Returns:
            Workflow result with LLM validation and review queue status
        """
        logger.info(f"Starting validation workflow for {model_name}")

        # Phase 1: LLM Validation
        llm_result = self.llm_validator.validate_context_file(context_file)

        # Determine if human review is needed
        human_review_required = not llm_result.is_valid or llm_result.confidence < 0.85

        if human_review_required:
            # Phase 2: Add to review queue
            review_item = self.review_queue.add_item(
                file_path=context_file,
                model_name=model_name,
                llm_confidence=llm_result.confidence,
                llm_issues_count=len(llm_result.issues),
            )
            review_priority = review_item.priority
            logger.info(
                f"Context added to review queue (priority: {review_priority.value})"
            )
        else:
            review_priority = ReviewPriority.LOW
            logger.info("Context passed LLM validation with high confidence")

        # Determine final status (before human review)
        final_status = (
            ReviewDecision.PENDING if human_review_required else ReviewDecision.APPROVED
        )

        return ValidationWorkflowResult(
            model_name=model_name,
            llm_validation=llm_result,
            human_review_required=human_review_required,
            review_priority=review_priority,
            final_status=final_status,
            is_approved=not human_review_required,
        )

    def validate_all_contexts(self, models_dir: str = "models") -> list[ValidationWorkflowResult]:
        """
        Validate all context files in the models directory.

        Args:
            models_dir: Root directory containing models

        Returns:
            List of workflow results for all contexts
        """
        results = []
        models_path = Path(models_dir)

        if not models_path.exists():
            logger.warning(f"Models directory not found: {models_dir}")
            return results

        # Find all .context.md files
        context_files = list(models_path.rglob("*.context.md"))
        logger.info(f"Found {len(context_files)} context files")

        for context_file in context_files:
            # Extract model name from context file (e.g., dim_customers.context.md -> dim_customers)
            model_name = context_file.stem.replace(".context", "")

            result = self.validate_context(str(context_file), model_name)
            results.append(result)

        return results

    def get_validation_report(self) -> dict:
        """
        Generate a validation report.

        Returns:
            Dictionary with validation statistics and insights
        """
        queue_stats = self.review_queue.get_statistics()
        pending_items = self.review_queue.get_queue(status=ReviewDecision.PENDING)

        report = {
            "summary": {
                "total_contexts_queued": queue_stats["total_items"],
                "pending_review": queue_stats["pending"],
                "approved": queue_stats["approved"],
                "rejected": queue_stats["rejected"],
                "needs_revision": queue_stats["needs_revision"],
            },
            "by_priority": queue_stats["by_priority"],
            "pending_items": [
                {
                    "model": item.model_name,
                    "confidence": item.llm_confidence,
                    "issues": item.llm_issues_count,
                    "priority": item.priority.value,
                    "assigned_to": item.assigned_to,
                    "created_at": item.created_at,
                }
                for item in pending_items[:10]  # Top 10
            ],
        }

        return report

    def get_pending_reviews(self) -> list[dict]:
        """
        Get list of contexts pending human review.

        Returns:
            List of pending review items
        """
        items = self.review_queue.get_queue(status=ReviewDecision.PENDING)

        return [
            {
                "model_name": item.model_name,
                "file_path": item.file_path,
                "priority": item.priority.value,
                "llm_confidence": item.llm_confidence,
                "issues_count": item.llm_issues_count,
                "assigned_to": item.assigned_to,
                "created_at": item.created_at,
            }
            for item in items
        ]

    def assign_context_for_review(self, model_name: str, reviewer: str) -> bool:
        """
        Assign a context to a specific reviewer.

        Args:
            model_name: Name of the model
            reviewer: Name of the reviewer

        Returns:
            True if assignment successful
        """
        success = self.review_queue.assign_to_reviewer(model_name, reviewer)
        if success:
            logger.info(f"Assigned {model_name} to {reviewer} for review")
        return success

    def approve_context(
        self,
        model_name: str,
        reviewer: str,
        comments: str = "",
    ) -> bool:
        """
        Approve a context after human review.

        Args:
            model_name: Model name
            reviewer: Reviewer name
            comments: Optional review comments

        Returns:
            True if successful
        """
        from .human_review import ReviewComment

        comment = ReviewComment(
            reviewer=reviewer,
            timestamp="",  # Will be set by submit_review
            comment=comments,
            severity="info",
        ) if comments else None

        return self.review_queue.submit_review(
            model_name=model_name,
            decision=ReviewDecision.APPROVED,
            reviewer=reviewer,
            comments=[comment] if comment else [],
            approved_sections=["all"],
            rejected_sections=[],
            revision_requests=[],
        )

    def reject_context(
        self,
        model_name: str,
        reviewer: str,
        reason: str,
        rejected_sections: list[str],
    ) -> bool:
        """
        Reject a context after human review.

        Args:
            model_name: Model name
            reviewer: Reviewer name
            reason: Reason for rejection
            rejected_sections: Sections that were rejected

        Returns:
            True if successful
        """
        from .human_review import ReviewComment

        comment = ReviewComment(
            reviewer=reviewer,
            timestamp="",
            comment=reason,
            severity="critical",
        )

        return self.review_queue.submit_review(
            model_name=model_name,
            decision=ReviewDecision.REJECTED,
            reviewer=reviewer,
            comments=[comment],
            approved_sections=[],
            rejected_sections=rejected_sections,
            revision_requests=[],
        )

    def request_revision(
        self,
        model_name: str,
        reviewer: str,
        revision_requests: list[str],
    ) -> bool:
        """
        Request revisions to a context.

        Args:
            model_name: Model name
            reviewer: Reviewer name
            revision_requests: List of revision requests

        Returns:
            True if successful
        """
        return self.review_queue.submit_review(
            model_name=model_name,
            decision=ReviewDecision.NEEDS_REVISION,
            reviewer=reviewer,
            comments=[],
            approved_sections=[],
            rejected_sections=[],
            revision_requests=revision_requests,
        )
