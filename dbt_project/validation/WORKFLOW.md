# Context Validation Workflow

Comprehensive validation system for dbt context files combining **LLM-as-Judge** with **Human Review**.

## 🎯 Overview

This workflow ensures that all dbt context files (`.context.md`) are:
1. **Structurally complete** — Contain all required sections
2. **Properly documented** — Explain business purpose, transformations, and quality rules
3. **Peer-reviewed** — Approved by domain experts before merging

```
Context File
    ↓
LLM Validation (Automatic)
    ↓
├─ Valid + High Confidence → APPROVED ✅
└─ Issues Found or Low Confidence → Human Review Queue
    ↓
Human Review (Manual)
    ↓
├─ APPROVED → Merge ✅
├─ REJECTED → Return to Author ❌
└─ NEEDS_REVISION → Request Changes 🔄
```

## 📋 Validation Phases

### Phase 1: LLM Validation (Automatic)

The LLM validator checks for:

- **Has Objectives** ✓ Clear business purpose and grain
- **Has Source Info** ✓ Documentation of source tables and lineage
- **Has Transformations** ✓ Explanation of logic applied
- **Has Field Catalog** ✓ All expected fields with types defined
- **Has Quality Rules** ✓ Tests and validation rules
- **Completeness** ✓ Adequate detail in all sections
- **Clarity** ✓ Clear, unambiguous writing

**Output:**
- `is_valid` — True if all critical sections present
- `confidence` — 0-1 score (higher = better)
- `issues` — List of validation issues with severity levels
- `summary` — Human-readable result

**Severity Levels:**
- 🔴 **CRITICAL** — Missing required sections or critical flaws
- 🟠 **HIGH** — Important information missing or unclear
- 🟡 **MEDIUM** — Good to have information missing
- ℹ️ **LOW** — Minor improvements suggested

### Phase 2: Human Review (Conditional)

Contexts go to human review if:
- LLM validation found critical/high issues, OR
- LLM confidence < 85%

**Reviewers approve/reject based on:**
- Does context accurately describe the model?
- Are transformations correctly documented?
- Are business assumptions clearly stated?
- Are data quality rules appropriate?
- Is writing clear and professional?

**Review Outcomes:**
- ✅ **APPROVED** — Context is correct and complete
- ❌ **REJECTED** — Context has significant flaws
- 🔄 **NEEDS_REVISION** — Minor fixes requested

## 🚀 Usage

### Validate a Single Context File

```python
from dbt_project.validation import ContextValidationOrchestrator

orchestrator = ContextValidationOrchestrator()

# Validate a single context
result = orchestrator.validate_context(
    "models/marts/dim_customers.context.md",
    "dim_customers"
)

print(f"Valid: {result.is_valid}")
print(f"Confidence: {result.llm_validation.confidence}")
print(f"Review Required: {result.human_review_required}")
```

### Validate All Contexts

```python
# Validate entire models directory
results = orchestrator.validate_all_contexts("dbt_project/models")

for result in results:
    print(f"{result.model_name}: {result.final_status}")
```

### Get Validation Report

```python
report = orchestrator.get_validation_report()

print(f"Total queued: {report['summary']['total_contexts_queued']}")
print(f"Pending review: {report['summary']['pending_review']}")
print(f"Approved: {report['summary']['approved']}")
```

### Assign for Review

```python
# Assign a context to a reviewer
orchestrator.assign_context_for_review(
    "dim_customers",
    "reviewer@example.com"
)
```

### Submit Review Decision

```python
# Approve a context
orchestrator.approve_context(
    "dim_customers",
    "reviewer@example.com",
    "Context is complete and accurate"
)

# Request revisions
orchestrator.request_revision(
    "dim_customers",
    "reviewer@example.com",
    revision_requests=[
        "Clarify data lineage in Source section",
        "Add examples to transformations",
    ]
)

# Reject a context
orchestrator.reject_context(
    "dim_customers",
    "reviewer@example.com",
    "Missing critical transformations documentation",
    rejected_sections=["Transformations"]
)
```

## 📊 Review Queue Management

### Queue Priority Levels

Contexts are prioritized in the review queue based on:

| Priority | LLM Confidence | Issues | Reason |
|----------|---------------|--------|--------|
| 🔴 CRITICAL | < 0.3 | > 5 | High risk, many issues |
| 🟠 HIGH | < 0.6 | > 2 | Significant problems |
| 🟡 MEDIUM | < 0.85 | > 0 | Minor issues |
| 🟢 LOW | ≥ 0.85 | 0 | Can auto-approve |

### Get Pending Reviews

```python
pending = orchestrator.get_pending_reviews()

for review in pending:
    print(f"{review['model_name']}: {review['priority']}")
    print(f"  Issues: {review['issues_count']}")
    print(f"  Assigned to: {review['assigned_to']}")
```

### Queue Statistics

```python
stats = orchestrator.review_queue.get_statistics()

print(f"Total: {stats['total_items']}")
print(f"Pending: {stats['pending']}")
print(f"By priority: {stats['by_priority']}")
```

## 🔑 Key Concepts

### Context File Structure

A complete context file (`.context.md`) should contain:

```markdown
# Context - [Model Name]

## Objectifs

Describe the business purpose and grain.

**Grain**: One row per [key], [key]

## Source

Document source tables and lineage.

- Table: `schema.table_name`
- Frequency: Daily/Hourly/Real-time
- Owner: Team name

## Transformations

Explain transformations applied.

1. Step 1: Description
2. Step 2: Description

**Exclusions**: Any filters or exclusions applied

## Champs (Columns)

List all expected fields.

| Field | Type | Description |
|-------|------|-------------|
| customer_id | STRING | Unique identifier |
| name | STRING | Customer name |

## Tests et Validations

Define data quality rules.

- PRIMARY KEY: customer_id
- NOT NULL: customer_id, name
- UNIQUE: customer_id
- ACCEPTED_VALUES: status IN ('active', 'inactive')

## Notes

Any additional context or assumptions.

**Last Updated**: YYYY-MM-DD
**Owner**: Name/Team
**Reviewer**: Name (optional)
```

### LLM Confidence Score

Score interpretation:
- `0.9+` — Excellent, auto-approve
- `0.7-0.9` — Good, might need minor review
- `0.5-0.7` — Acceptable, human review recommended
- `0.3-0.5` — Poor, definitely needs review
- `< 0.3` — Critical issues, needs rework

## 🔗 Integration with CI/CD

### GitHub Actions Workflow

Add to `.github/workflows/validation.yml`:

```yaml
name: Context Validation

on: [pull_request, push]

jobs:
  validate-contexts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: uv sync --all-groups
      
      - name: Validate contexts
        run: |
          python -c "
          from dbt_project.validation import ContextValidationOrchestrator
          orchestrator = ContextValidationOrchestrator()
          results = orchestrator.validate_all_contexts('dbt_project/models')
          
          # Fail if any critical issues
          critical = [r for r in results if not r.is_valid]
          if critical:
              print(f'❌ {len(critical)} contexts have critical issues')
              exit(1)
          print(f'✅ All contexts validated')
          "
```

## 📚 Examples

### Example 1: Complete Context (Auto-Approved)

```markdown
# Context - dim_customers

## Objectifs

Provide a single source of truth for customer master data.

**Grain**: One row per unique customer_id

## Source

- **Table**: `raw.salesforce_accounts`
- **Frequency**: Daily snapshot
- **Owner**: Sales Operations

## Transformations

1. Deduplication: Keep latest record per customer_id
2. Standardization: Normalize phone numbers and emails
3. Enrichment: Add country from account address

**Exclusions**: Test accounts (account_name LIKE '%test%')

## Champs

| Field | Type | Description |
|-------|------|-------------|
| customer_id | STRING | Salesforce account ID (primary key) |
| name | STRING | Account name, standardized |
| country | STRING | Derived from address |
| created_at | TIMESTAMP | Account creation date |
| status | STRING | active \| churned \| prospect |

## Tests et Validations

- PRIMARY KEY: customer_id
- NOT NULL: customer_id, name, created_at
- UNIQUE: customer_id
- ACCEPTED_VALUES: status IN ('active', 'churned', 'prospect')
- RELATIONSHIPS: foreign key to dim_accounts.account_id

## Notes

Created for Sales Analytics Team.
Replaces legacy customer_master table.

**Last Updated**: 2026-04-23
**Owner**: Analytics Team
```

**Result**: ✅ Valid + Auto-Approved (confidence: 0.95)

### Example 2: Incomplete Context (Requires Review)

```markdown
# Context - fct_orders

Order transactions.

## Source

Orders table.

## Champs

- order_id: ID
- amount: Total
- date: When ordered
```

**Issues Found**:
- 🔴 Missing clear objectives/grain
- 🟠 Missing transformations documentation
- 🟠 Missing data quality rules
- 🟡 Field descriptions too brief

**Result**: ❌ Needs Human Review (confidence: 0.42, priority: CRITICAL)

## 🎓 Best Practices

1. **Write complete contexts first** — Don't wait for LLM feedback
2. **Include examples** — Help reviewers understand transformations
3. **Document assumptions** — Explain business logic clearly
4. **Test your models** — Quality rules should match dbt tests
5. **Get peer review** — Better context = better data quality

## 🚨 Troubleshooting

**Q: My context is valid but LLM still flags it**
→ Check for spelling/grammar issues, use clear markdown headers

**Q: How long does human review take?**
→ Priority-based: CRITICAL (1 day), HIGH (2-3 days), MEDIUM (1 week)

**Q: Can I auto-approve without human review?**
→ Only if LLM confidence > 90% and no critical issues

**Q: What if reviewers disagree?**
→ Escalate to data governance team or document as "approved with comments"

---

**Last Updated**: 2026-04-23  
**Maintainer**: OpenClaw Context Platform Team
