# Context Validation Module

LLM-powered validation system for dbt context files with human review workflow.

## 🎯 Quick Start

### Installation

```bash
# Dependencies are in pyproject.toml
uv sync --all-groups
```

### Validate Contexts

```bash
# Validate single file
python -m dbt_project.validation.cli validate --file models/marts/dim_customers.context.md

# Validate entire directory
python -m dbt_project.validation.cli validate --directory dbt_project/models
```

### Check Review Queue

```bash
# See pending reviews
python -m dbt_project.validation.cli pending

# Generate report
python -m dbt_project.validation.cli report
```

### Submit Review

```bash
# Approve a context
python -m dbt_project.validation.cli approve dim_customers reviewer@example.com -c "Looks good!"

# Request revisions
python -m dbt_project.validation.cli revision dim_customers reviewer@example.com "Clarify transformations,Add examples"

# Reject a context
python -m dbt_project.validation.cli reject dim_customers reviewer@example.com "Missing critical sections" -s "Transformations,Quality"
```

## 📦 Module Structure

```
validation/
├── __init__.py                 # Public API
├── llm_validator.py           # LLM validation logic
├── human_review.py            # Review queue and decisions
├── orchestrator.py            # Workflow orchestration
├── cli.py                     # Command-line interface
├── WORKFLOW.md               # Detailed workflow documentation
└── README.md                 # This file
```

## 🔧 API Usage

### Basic Validation

```python
from dbt_project.validation import ContextValidationOrchestrator

# Initialize
orchestrator = ContextValidationOrchestrator()

# Validate a context file
result = orchestrator.validate_context(
    "models/marts/dim_customers.context.md",
    "dim_customers"
)

print(f"Valid: {result.is_valid}")
print(f"Confidence: {result.llm_validation.confidence}")
print(f"Issues: {len(result.llm_validation.issues)}")
```

### Get Pending Reviews

```python
pending = orchestrator.get_pending_reviews()

for review in pending:
    print(f"{review['model_name']}: {review['priority']}")
```

### Submit Review Decision

```python
# Approve
orchestrator.approve_context("dim_customers", "reviewer@example.com")

# Reject
orchestrator.reject_context(
    "dim_customers",
    "reviewer@example.com",
    "Missing transformations documentation",
    ["Transformations"]
)

# Request revisions
orchestrator.request_revision(
    "dim_customers",
    "reviewer@example.com",
    ["Add more detailed transformation steps"]
)
```

## 📊 Validation Flow

1. **LLM Analysis**
   - Checks for required sections
   - Validates completeness
   - Assigns confidence score
   - Lists any issues found

2. **Auto-Approval** (if confident)
   - Confidence > 85% + no critical issues
   - Automatically approved

3. **Review Queue** (if needed)
   - Added to human review queue
   - Prioritized by severity
   - Assigned to reviewer

4. **Human Review**
   - Reviewer checks context
   - Decides: Approve, Reject, or Request Revision
   - Provides feedback

5. **Final Status**
   - Context marked as approved/rejected
   - Author notified of decision

## 🔑 Key Classes

### LLMContextValidator

Validates context files using configurable criteria.

```python
validator = LLMContextValidator()
result = validator.validate_context_file("path/to/context.md")

# Result contains:
# - is_valid (bool)
# - confidence (0-1)
# - issues (list of ValidationIssue)
# - summary (str)
# - metadata (dict)
```

### HumanReviewQueue

Manages review queue with priority-based ordering.

```python
queue = HumanReviewQueue()

# Add to queue
queue.add_item(
    file_path="models/dim_customers.context.md",
    model_name="dim_customers",
    llm_confidence=0.65,
    llm_issues_count=3
)

# Get pending
pending = queue.get_queue(status=ReviewDecision.PENDING)

# Submit review
queue.submit_review(
    model_name="dim_customers",
    decision=ReviewDecision.APPROVED,
    reviewer="reviewer@example.com",
    comments=[],
    approved_sections=["all"],
    rejected_sections=[],
    revision_requests=[]
)
```

### ContextValidationOrchestrator

Orchestrates the complete validation workflow.

```python
orchestrator = ContextValidationOrchestrator()

# Full validation workflow
result = orchestrator.validate_context("models/dim.context.md", "dim")

# Get report
report = orchestrator.get_validation_report()

# Manage reviews
orchestrator.assign_context_for_review("dim", "reviewer@example.com")
orchestrator.approve_context("dim", "reviewer@example.com")
```

## 📝 Context File Format

See [WORKFLOW.md](./WORKFLOW.md#-context-file-structure) for complete format.

Minimum required:

```markdown
# Context - [Model Name]

## Objectifs

Clear business purpose and grain.

## Source

Source table and lineage.

## Champs

Expected fields and types.

## Tests et Validations

Data quality rules.
```

## 🧪 Testing

```bash
# Run tests
uv run pytest tests/test_context_validation.py -v

# With coverage
uv run pytest tests/test_context_validation.py --cov=dbt_project.validation
```

## 🔌 Integration Points

### dbt Parsing

The validation system can integrate with dbt to:
- Automatically validate contexts for parsed models
- Compare model structure with documented fields
- Validate that dbt tests match documented quality rules

### Git Hooks (Pre-commit)

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: validate-contexts
      name: Validate context files
      entry: python -m dbt_project.validation.cli validate --directory dbt_project/models
      language: system
      files: \.context\.md$
```

### CI/CD Pipeline

Add to GitHub Actions or your CI tool:

```yaml
- name: Validate contexts
  run: python -m dbt_project.validation.cli validate --directory dbt_project/models
```

## 🎓 Examples

### Example 1: Auto-Approved Context

```
File: dim_customers.context.md

Validation Result:
✅ PASS (Confidence: 95%)
No issues found
Status: APPROVED (no human review needed)
```

### Example 2: Context Needing Review

```
File: fct_orders.context.md

Validation Result:
❌ Issues found (Confidence: 42%)
- 🔴 Missing "Objectifs" section
- 🟠 Incomplete "Champs" documentation
- 🟡 No data quality rules defined

Status: PENDING (added to review queue)
Priority: CRITICAL
```

## 🚨 Troubleshooting

**Q: LLM is too strict/lenient**
→ Modify validation criteria in `llm_validator.py`

**Q: How to override auto-approval threshold?**
→ Pass `confidence_threshold` to orchestrator

**Q: How to manually validate without LLM?**
→ Create context files and submit for direct human review

**Q: Storage location for review queue?**
→ Default: `.review_queue/` in project root (customizable)

## 📚 Related Documentation

- [WORKFLOW.md](./WORKFLOW.md) — Detailed workflow documentation
- [../BEST_PRACTICES.md](../BEST_PRACTICES.md) — Project best practices
- [../README.md](../README.md) — Project overview

## 🔄 Future Enhancements

- [ ] Integration with Claude API for real LLM validation
- [ ] Web UI for managing reviews
- [ ] Slack/email notifications for reviewers
- [ ] Automated feedback suggestions
- [ ] Version history of context changes
- [ ] Metrics and analytics dashboard
