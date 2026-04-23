"""
Human Review System

Manages the human review queue for context validation results.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ReviewDecision(Enum):
    """Possible review decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    PENDING = "pending"


class ReviewPriority(Enum):
    """Priority levels for review queue."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReviewComment:
    """A single review comment."""

    reviewer: str
    timestamp: str
    comment: str
    severity: str  # "critical", "warning", "info"


@dataclass
class HumanReview:
    """Record of human review."""

    file_path: str
    decision: ReviewDecision
    reviewer: str
    timestamp: str
    comments: list[ReviewComment]
    approved_sections: list[str]
    rejected_sections: list[str]
    revision_requests: list[str]


@dataclass
class ReviewQueueItem:
    """Item in the human review queue."""

    file_path: str
    model_name: str
    llm_confidence: float
    llm_issues_count: int
    priority: ReviewPriority
    created_at: str
    assigned_to: Optional[str] = None
    status: ReviewDecision = ReviewDecision.PENDING
    review: Optional[HumanReview] = None


class HumanReviewQueue:
    """
    Manages the queue of contexts awaiting human review.

    Items are prioritized based on:
    - LLM confidence (lower = higher priority)
    - Severity of issues (critical/high = higher priority)
    - Assignment status
    """

    def __init__(self, storage_path: str = ".review_queue"):
        """
        Initialize review queue.

        Args:
            storage_path: Where to store queue items and reviews
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.queue_file = self.storage_path / "queue.jsonl"
        self.reviews_dir = self.storage_path / "reviews"
        self.reviews_dir.mkdir(exist_ok=True)

    def add_item(
        self,
        file_path: str,
        model_name: str,
        llm_confidence: float,
        llm_issues_count: int,
    ) -> ReviewQueueItem:
        """
        Add item to review queue.

        Args:
            file_path: Path to context file
            model_name: Name of the dbt model
            llm_confidence: LLM validation confidence (0-1)
            llm_issues_count: Number of issues found

        Returns:
            The created queue item
        """
        # Determine priority based on confidence and issues
        if llm_confidence < 0.3 or llm_issues_count > 5:
            priority = ReviewPriority.CRITICAL
        elif llm_confidence < 0.6 or llm_issues_count > 2:
            priority = ReviewPriority.HIGH
        elif llm_confidence < 0.85 or llm_issues_count > 0:
            priority = ReviewPriority.MEDIUM
        else:
            priority = ReviewPriority.LOW

        item = ReviewQueueItem(
            file_path=file_path,
            model_name=model_name,
            llm_confidence=llm_confidence,
            llm_issues_count=llm_issues_count,
            priority=priority,
            created_at=datetime.now().isoformat(),
        )

        # Append to queue
        with open(self.queue_file, "a") as f:
            item_dict = asdict(item)
            # Convert enums to strings for JSON serialization
            item_dict["status"] = item_dict["status"].value
            item_dict["priority"] = item_dict["priority"].value
            f.write(json.dumps(item_dict) + "\n")

        logger.info(
            f"Added to review queue: {model_name} (priority: {priority.value})"
        )
        return item

    def get_queue(
        self,
        priority: Optional[ReviewPriority] = None,
        status: Optional[ReviewDecision] = None,
    ) -> list[ReviewQueueItem]:
        """
        Get items from queue with optional filtering.

        Args:
            priority: Filter by priority level
            status: Filter by review status

        Returns:
            List of queue items
        """
        items = []

        if not self.queue_file.exists():
            return items

        with open(self.queue_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)

                # Convert back to enums
                data["status"] = ReviewDecision(data["status"])
                data["priority"] = ReviewPriority(data["priority"])

                if priority and data["priority"] != priority:
                    continue
                if status and data["status"] != status:
                    continue

                items.append(ReviewQueueItem(**data))

        # Sort by priority and creation date
        priority_order = {
            ReviewPriority.CRITICAL: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.LOW: 3,
        }
        items.sort(
            key=lambda x: (
                priority_order.get(x.priority, 4),
                x.created_at,
            )
        )

        return items

    def assign_to_reviewer(self, model_name: str, reviewer: str) -> bool:
        """
        Assign a context to a specific reviewer.

        Args:
            model_name: Model name
            reviewer: Reviewer name/id

        Returns:
            True if successful
        """
        items = self.get_queue(status=ReviewDecision.PENDING)

        updated = False
        for item in items:
            if model_name in item.model_name:
                item.assigned_to = reviewer
                updated = True
                logger.info(f"Assigned {model_name} to {reviewer}")

        if updated:
            self._save_queue(items)

        return updated

    def submit_review(
        self,
        model_name: str,
        decision: ReviewDecision,
        reviewer: str,
        comments: list[ReviewComment],
        approved_sections: list[str],
        rejected_sections: list[str],
        revision_requests: list[str],
    ) -> bool:
        """
        Submit a human review.

        Args:
            model_name: Model name being reviewed
            decision: Review decision
            reviewer: Reviewer name
            comments: List of review comments
            approved_sections: Approved sections
            rejected_sections: Rejected sections
            revision_requests: Sections requesting revision

        Returns:
            True if successful
        """
        items = self.get_queue()

        for item in items:
            if model_name in item.model_name:
                review = HumanReview(
                    file_path=item.file_path,
                    decision=decision,
                    reviewer=reviewer,
                    timestamp=datetime.now().isoformat(),
                    comments=comments,
                    approved_sections=approved_sections,
                    rejected_sections=rejected_sections,
                    revision_requests=revision_requests,
                )

                item.status = decision
                item.review = review

                # Save review to file
                review_file = (
                    self.reviews_dir
                    / f"{item.model_name}_{datetime.now().timestamp()}.json"
                )
                with open(review_file, "w") as f:
                    review_dict = asdict(review)
                    # Convert enums to strings
                    review_dict["decision"] = review_dict["decision"].value
                    json.dump(review_dict, f, indent=2, default=str)

                logger.info(f"Review submitted for {model_name}: {decision.value}")
                break

        self._save_queue(items)
        return True

    def _save_queue(self, items: list[ReviewQueueItem]):
        """Save queue back to file."""
        with open(self.queue_file, "w") as f:
            for item in items:
                item_dict = asdict(item)
                # Convert enums to strings for JSON serialization
                item_dict["status"] = item_dict["status"].value
                item_dict["priority"] = item_dict["priority"].value
                f.write(json.dumps(item_dict, default=str) + "\n")

    def get_statistics(self) -> dict:
        """Get queue statistics."""
        items = self.get_queue()

        return {
            "total_items": len(items),
            "pending": len([i for i in items if i.status == ReviewDecision.PENDING]),
            "approved": len([i for i in items if i.status == ReviewDecision.APPROVED]),
            "rejected": len([i for i in items if i.status == ReviewDecision.REJECTED]),
            "needs_revision": len(
                [i for i in items if i.status == ReviewDecision.NEEDS_REVISION]
            ),
            "by_priority": {
                "critical": len([i for i in items if i.priority == ReviewPriority.CRITICAL]),
                "high": len([i for i in items if i.priority == ReviewPriority.HIGH]),
                "medium": len([i for i in items if i.priority == ReviewPriority.MEDIUM]),
                "low": len([i for i in items if i.priority == ReviewPriority.LOW]),
            },
        }
