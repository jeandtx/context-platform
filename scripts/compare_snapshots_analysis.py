#!/usr/bin/env python3
"""
Snapshot Change Analysis Script

Compares snapshot tables against their source models to calculate:
- Number of changed rows (dbt_valid_to IS NOT NULL)
- Total rows in original model
- Percentage of changed rows

Usage:
    python compare_snapshots_analysis.py
    python compare_snapshots_analysis.py --output report.md
    python compare_snapshots_analysis.py --json
"""

import argparse
import json
import os
from datetime import datetime

import duckdb


class SnapshotAnalyzer:
    """Analyzes dbt snapshot tables for data changes."""

    def __init__(
        self,
        db_path: str = "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt.duckdb",
    ):
        """Initialize connection to DuckDB database."""
        self.db_path = db_path
        self.conn = duckdb.connect(db_path, read_only=True)
        self.snapshots = [
            "snapshots.snapshot_dim_countries",
            "snapshots.snapshot_dim_matches",
            "snapshots.snapshot_dim_population",
            "snapshots.snapshot_dim_team_country",
            "snapshots.snapshot_dim_teams",
            "snapshots.snapshot_fact_country_performance",
            "snapshots.snapshot_kpi_performance_vs_population",
            "snapshots.snapshot_stg_country_codes",
            "snapshots.snapshot_stg_events",
            "snapshots.snapshot_stg_indicators",
            "snapshots.snapshot_stg_matches",
        ]

    def get_snapshot_source_model(self, snapshot_name: str) -> str:
        """Extract the source model name from snapshot name."""
        # Remove 'snapshot_' prefix to get model name
        model_name = snapshot_name.replace("snapshots.snapshot_", "")
        return model_name

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            self.conn.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            return True
        except Exception:
            return False

    def get_total_rows(self, table_name: str) -> int:
        """Get total row count for a table."""
        try:
            result = self.conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchall()
            return result[0][0] if result else 0
        except Exception as e:
            print(f"Error counting rows in {table_name}: {e}")
            return 0

    def get_changed_rows(self, snapshot_table: str) -> int:
        """Get count of changed rows (where dbt_valid_to IS NOT NULL)."""
        try:
            result = self.conn.execute(
                f"SELECT COUNT(*) as count FROM {snapshot_table} WHERE dbt_valid_to IS NOT NULL"
            ).fetchall()
            return result[0][0] if result else 0
        except Exception as e:
            print(f"Error counting changed rows in {snapshot_table}: {e}")
            return 0

    def analyze_snapshot(self, snapshot_name: str) -> dict:
        """Analyze a single snapshot and return statistics."""
        if not self.table_exists(snapshot_name):
            return {
                "snapshot": snapshot_name,
                "status": "ERROR",
                "error": f"Snapshot table '{snapshot_name}' not found",
                "source_model": self.get_snapshot_source_model(snapshot_name),
            }

        source_model = self.get_snapshot_source_model(snapshot_name)

        # Get counts
        total_snapshot_rows = self.get_total_rows(snapshot_name)
        changed_rows = self.get_changed_rows(snapshot_name)
        source_total_rows = (
            self.get_total_rows(source_model) if self.table_exists(source_model) else 0
        )

        # Calculate percentage
        change_percentage = changed_rows / source_total_rows * 100 if source_total_rows > 0 else 0.0

        return {
            "snapshot": snapshot_name,
            "source_model": source_model,
            "status": "OK",
            "total_snapshot_rows": total_snapshot_rows,
            "changed_rows": changed_rows,
            "source_model_rows": source_total_rows,
            "change_percentage": round(change_percentage, 2),
            "source_model_exists": self.table_exists(source_model),
        }

    def run_analysis(self) -> list[dict]:
        """Run analysis on all snapshots."""
        results = []
        for snapshot in self.snapshots:
            print(f"Analyzing {snapshot}...", end=" ")
            result = self.analyze_snapshot(snapshot)
            results.append(result)
            if result["status"] == "OK":
                print(
                    f"✓ ({result['changed_rows']} changed / {result['source_model_rows']} total = {result['change_percentage']}%)"
                )
            else:
                print(f"✗ {result.get('error', 'Unknown error')}")

        return results

    def close(self):
        """Close database connection."""
        self.conn.close()


def format_markdown_table(results: list[dict]) -> str:
    """Format results as a markdown table."""
    lines = [
        "# Snapshot Change Analysis Report\n",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "| Snapshot | Source Model | Total Rows | Changed Rows | % Changed |",
        "|----------|--------------|-----------|--------------|-----------|",
    ]

    for result in results:
        if result["status"] == "OK":
            pct = result["change_percentage"]
            changed = result["changed_rows"]
            total = result["source_model_rows"]
            lines.append(
                f"| {result['snapshot']} | {result['source_model']} | {total} | {changed} | {pct}% |"
            )
        else:
            lines.append(f"| {result['snapshot']} | ERROR | - | - | - |")

    # Add summary statistics
    ok_results = [r for r in results if r["status"] == "OK"]
    if ok_results:
        total_changed = sum(r["changed_rows"] for r in ok_results)
        total_rows = sum(r["source_model_rows"] for r in ok_results)
        avg_percentage = (total_changed / total_rows * 100) if total_rows > 0 else 0

        lines.extend(
            [
                "\n## Summary Statistics\n",
                f"- Total Models Analyzed: {len(ok_results)}",
                f"- Total Changed Rows: {total_changed:,}",
                f"- Total Rows in Models: {total_rows:,}",
                f"- Average Change Rate: {round(avg_percentage, 2)}%",
            ]
        )

    return "\n".join(lines)


def format_console_output(results: list[dict]) -> str:
    """Format results for console output."""
    lines = [
        "\n" + "=" * 80,
        "SNAPSHOT CHANGE ANALYSIS REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        "",
    ]

    for result in results:
        if result["status"] == "OK":
            lines.append(f"📊 {result['snapshot']}")
            lines.append(f"   Source Model: {result['source_model']}")
            lines.append(f"   Total Rows (Source): {result['source_model_rows']:,}")
            lines.append(f"   Changed Rows: {result['changed_rows']:,}")
            lines.append(f"   Change Percentage: {result['change_percentage']}%")
            lines.append("")
        else:
            lines.append(f"❌ {result['snapshot']}: {result.get('error', 'Unknown error')}")
            lines.append("")

    # Summary
    ok_results = [r for r in results if r["status"] == "OK"]
    if ok_results:
        total_changed = sum(r["changed_rows"] for r in ok_results)
        total_rows = sum(r["source_model_rows"] for r in ok_results)
        avg_percentage = (total_changed / total_rows * 100) if total_rows > 0 else 0

        lines.extend(
            [
                "=" * 80,
                "SUMMARY",
                "=" * 80,
                f"Models Analyzed: {len(ok_results)}",
                f"Total Changed Rows: {total_changed:,}",
                f"Total Rows in Models: {total_rows:,}",
                f"Average Change Rate: {round(avg_percentage, 2)}%",
                "=" * 80,
            ]
        )

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze dbt snapshots to calculate percentage of changed records"
    )
    parser.add_argument(
        "--db",
        default="/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt.duckdb",
        help="Path to DuckDB database (default: dbt.duckdb)",
    )
    parser.add_argument("--output", "-o", help="Output file for markdown report")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Check if database exists
    if not os.path.exists(args.db):
        print(f"Error: Database file '{args.db}' not found")
        return 1

    # Run analysis
    analyzer = SnapshotAnalyzer(args.db)
    print(f"Connected to {args.db}")
    print(f"Analyzing {len(analyzer.snapshots)} snapshots...\n")

    results = analyzer.run_analysis()
    analyzer.close()

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.output:
        markdown_report = format_markdown_table(results)
        with open(args.output, "w") as f:
            f.write(markdown_report)
        print(f"\n✓ Report saved to {args.output}")
    else:
        print(format_console_output(results))

    return 0


if __name__ == "__main__":
    exit(main())
