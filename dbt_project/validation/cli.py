"""
CLI for context validation workflow.

Usage:
    python -m dbt_project.validation.cli validate models/
    python -m dbt_project.validation.cli report
    python -m dbt_project.validation.cli pending
"""

import argparse
import json
import logging
from pathlib import Path
from tabulate import tabulate

from .orchestrator import ContextValidationOrchestrator
from .llm_validator import LLMContextValidator
from .human_review import HumanReviewQueue, ReviewDecision

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def validate_command(args):
    """Run validation on context files."""
    orchestrator = ContextValidationOrchestrator()

    if args.file:
        # Validate single file
        model_name = Path(args.file).stem.replace(".context", "")
        logger.info(f"Validating {args.file}...")

        result = orchestrator.validate_context(args.file, model_name)
        print_validation_result(result)
    else:
        # Validate all contexts in directory
        models_dir = args.directory or "dbt_project/models"
        logger.info(f"Validating all contexts in {models_dir}...")

        results = orchestrator.validate_all_contexts(models_dir)

        # Summary table
        table_data = []
        for r in results:
            table_data.append([
                r.model_name,
                "✅ PASS" if r.is_valid else "❌ FAIL",
                f"{r.llm_validation.confidence:.0%}",
                len(r.llm_validation.issues),
                "Yes" if r.human_review_required else "No",
            ])

        print("\n📋 Validation Results:")
        print(tabulate(
            table_data,
            headers=["Model", "Status", "Confidence", "Issues", "Review"],
            tablefmt="grid",
        ))

        # Summary stats
        valid = sum(1 for r in results if r.is_valid)
        total = len(results)
        print(f"\n✅ {valid}/{total} contexts passed LLM validation")


def report_command(args):
    """Generate validation report."""
    orchestrator = ContextValidationOrchestrator()
    report = orchestrator.get_validation_report()

    print("\n📊 Validation Report")
    print("=" * 60)

    # Summary
    summary = report["summary"]
    print(f"\nSummary:")
    print(f"  Total Contexts: {summary['total_contexts_queued']}")
    print(f"  ⏳ Pending Review: {summary['pending_review']}")
    print(f"  ✅ Approved: {summary['approved']}")
    print(f"  ❌ Rejected: {summary['rejected']}")
    print(f"  🔄 Needs Revision: {summary['needs_revision']}")

    # By priority
    print(f"\nBy Priority:")
    priority = report["by_priority"]
    for p, count in priority.items():
        if count > 0:
            icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            print(f"  {icons.get(p, '○')} {p.title()}: {count}")

    # Pending items
    if report["pending_items"]:
        print(f"\nTop Pending Items:")
        table_data = []
        for item in report["pending_items"]:
            table_data.append([
                item["model"],
                item["priority"],
                f"{item['confidence']:.0%}",
                item["issues"],
                item["assigned_to"] or "Unassigned",
            ])

        print(tabulate(
            table_data,
            headers=["Model", "Priority", "Confidence", "Issues", "Reviewer"],
            tablefmt="simple",
        ))


def pending_command(args):
    """List pending reviews."""
    orchestrator = ContextValidationOrchestrator()
    pending = orchestrator.get_pending_reviews()

    if not pending:
        print("✅ No pending reviews!")
        return

    print(f"\n⏳ {len(pending)} Pending Reviews:")
    print("=" * 60)

    table_data = []
    for item in pending:
        table_data.append([
            item["model_name"],
            item["priority"],
            f"{item['llm_confidence']:.0%}",
            item["issues_count"],
            item["assigned_to"] or "Unassigned",
            item["created_at"][:10],
        ])

    print(tabulate(
        table_data,
        headers=["Model", "Priority", "Confidence", "Issues", "Reviewer", "Created"],
        tablefmt="grid",
    ))


def assign_command(args):
    """Assign a context for review."""
    orchestrator = ContextValidationOrchestrator()

    success = orchestrator.assign_context_for_review(
        args.model,
        args.reviewer,
    )

    if success:
        print(f"✅ Assigned {args.model} to {args.reviewer}")
    else:
        print(f"❌ Failed to assign {args.model}")


def approve_command(args):
    """Approve a context."""
    orchestrator = ContextValidationOrchestrator()

    success = orchestrator.approve_context(
        args.model,
        args.reviewer,
        args.comment or "",
    )

    if success:
        print(f"✅ Approved {args.model}")
    else:
        print(f"❌ Failed to approve {args.model}")


def reject_command(args):
    """Reject a context."""
    orchestrator = ContextValidationOrchestrator()

    sections = args.sections.split(",") if args.sections else []

    success = orchestrator.reject_context(
        args.model,
        args.reviewer,
        args.reason,
        sections,
    )

    if success:
        print(f"❌ Rejected {args.model}")
    else:
        print(f"❌ Failed to reject {args.model}")


def revision_command(args):
    """Request revisions."""
    orchestrator = ContextValidationOrchestrator()

    requests = args.requests.split(",")

    success = orchestrator.request_revision(
        args.model,
        args.reviewer,
        requests,
    )

    if success:
        print(f"🔄 Revision requested for {args.model}")
    else:
        print(f"❌ Failed to request revisions")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Context Validation Workflow CLI",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate context files")
    validate_group = validate_parser.add_mutually_exclusive_group()
    validate_group.add_argument("--file", "-f", help="Validate single file")
    validate_group.add_argument("--directory", "-d", help="Directory with models")
    validate_parser.set_defaults(func=validate_command)

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate validation report")
    report_parser.set_defaults(func=report_command)

    # Pending command
    pending_parser = subparsers.add_parser("pending", help="List pending reviews")
    pending_parser.set_defaults(func=pending_command)

    # Assign command
    assign_parser = subparsers.add_parser("assign", help="Assign for review")
    assign_parser.add_argument("model", help="Model name")
    assign_parser.add_argument("reviewer", help="Reviewer email/name")
    assign_parser.set_defaults(func=assign_command)

    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve context")
    approve_parser.add_argument("model", help="Model name")
    approve_parser.add_argument("reviewer", help="Reviewer email/name")
    approve_parser.add_argument("--comment", "-c", help="Optional comment")
    approve_parser.set_defaults(func=approve_command)

    # Reject command
    reject_parser = subparsers.add_parser("reject", help="Reject context")
    reject_parser.add_argument("model", help="Model name")
    reject_parser.add_argument("reviewer", help="Reviewer email/name")
    reject_parser.add_argument("reason", help="Reason for rejection")
    reject_parser.add_argument("--sections", "-s", help="Comma-separated rejected sections")
    reject_parser.set_defaults(func=reject_command)

    # Revision command
    revision_parser = subparsers.add_parser("revision", help="Request revisions")
    revision_parser.add_argument("model", help="Model name")
    revision_parser.add_argument("reviewer", help="Reviewer email/name")
    revision_parser.add_argument("requests", help="Comma-separated revision requests")
    revision_parser.set_defaults(func=revision_command)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


def print_validation_result(result):
    """Pretty print validation result."""
    print("\n" + "=" * 60)
    print(f"Model: {result.model_name}")
    print(f"Status: {result.final_status.value.upper()}")
    print(f"Confidence: {result.llm_validation.confidence:.0%}")
    print(f"Review Required: {'Yes' if result.human_review_required else 'No'}")

    if result.llm_validation.issues:
        print(f"\nIssues ({len(result.llm_validation.issues)}):")
        for issue in result.llm_validation.issues:
            icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "ℹ️",
            }.get(issue.severity.value, "○")

            print(f"  {icon} [{issue.category}] {issue.message}")
            if issue.suggestion:
                print(f"     → {issue.suggestion}")

    print(f"\nSummary: {result.llm_validation.summary}")
    print("=" * 60)
