# DuckDB + dbt + Evidence.dev POC

A complete Proof of Concept demonstrating the integration of three powerful data tools:

- **DuckDB**: Fast in-process SQL OLAP database
- **dbt**: Data transformation tool for building analytics-ready data structures
- **Evidence.dev**: BI dashboard builder for creating web-based dashboards

## 🎯 Project Overview

This POC demonstrates a complete data pipeline:

```
Raw Data (CSV) → DuckDB → dbt Models → Evidence.dev Dashboard
```

The project includes:

- 8 sample customers with transactional data
- dbt models for data staging and transformation
- Data quality tests (uniqueness, not null constraints)
- An Evidence.dev dashboard with visualizations and metrics

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+ (for Evidence.dev)
- pip package manager
- Git

## 🚀 Quick Start

### 1. Clone and Setup the Repository

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project"
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# OR manually install:
pip install duckdb>=1.0.0 dbt-core>=1.8.0 dbt-duckdb>=1.8.0 evidence>=0.3.0
```

### 3. Build dbt Models

```bash
cd dbt_project
export DBT_PROFILES_DIR=../.dbt
dbt run      # Build all models
dbt test     # Run data quality tests
```

Expected output:

```
Finished running 1 table model, 2 view models in X seconds
Done. PASS=3 WARN=0 ERROR=0
Completed successfully
```

### 4. Validate the Complete Chain

```bash
cd ..
python validate_poc.py
```

This will display:

- ✅ DuckDB connection status
- 📊 Available tables/views (raw_customers, stg_customers, fct_customers)
- 📈 Sample customer data with segmentation
- 💰 Aggregated metrics by customer segment

### 5. Start the Evidence Dashboard

```bash
cd evidence
# Install Evidence CLI if not already installed
npm install -g @evidence-dev/cli

# Start the development server
evidence
```

Then open http://localhost:3000 in your browser to view the Customer Dashboard.

## 📁 Project Structure

```
.
├── README.md                          # This file
├── pyproject.toml                     # Python dependencies
├── validate_poc.py                    # Validation script
├── dbt.duckdb                         # DuckDB database file (auto-created)
│
├── .dbt/
│   └── profiles.yml                   # dbt profile configuration for DuckDB
│
├── dbt_project/                       # dbt project root
│   ├── dbt_project.yml                # dbt project configuration
│   ├── models/
│   │   ├── schema.yml                 # Model and test definitions
│   │   ├── staging/
│   │   │   ├── raw_customers.sql      # Raw data (SQL-based seed)
│   │   │   └── stg_customers.sql      # Staging transformation
│   │   └── marts/
│   │       └── fct_customers.sql      # Fact table with segmentation
│   ├── tests/                         # Custom dbt tests (if any)
│   ├── data/                          # Seed data (optional CSV files)
│   └── target/                        # Compiled models (auto-generated)
│
└── evidence/                          # Evidence.dev dashboard
    ├── evidence.yml                   # Evidence project configuration
    ├── package.json                   # Node.js dependencies
    ├── sources/
    │   └── duckdb.source.yml          # DuckDB data source configuration
    └── pages/
        └── customers.md               # Customer dashboard page
```

## 📊 Data Models

### raw_customers (View)

SQL-based seed table containing 8 sample customers with:

- id: Customer identifier
- name: Customer name
- email: Email address
- created_at: Account creation date
- amount: Order amount

### stg_customers (View)

Staging layer that:

- Renames 'amount' to 'order_amount'
- Provides a clean interface for downstream models
- Tests: unique ID, not null ID

### fct_customers (Table)

Fact table with business logic:

- Rounds order amounts to 2 decimal places
- Segments customers into 3 tiers:
    - **High Value**: $2,000+
    - **Medium Value**: $1,000-$1,999
    - **Low Value**: <$1,000
- Tests: unique ID, not null ID, not null order amount

## 🧪 Data Quality

The project includes 5 automated tests:

```bash
dbt test
```

Tests included:

1. `unique_stg_customers_id` - Verify customer IDs are unique in staging
2. `not_null_stg_customers_id` - Verify customer IDs are not null in staging
3. `unique_fct_customers_id` - Verify customer IDs are unique in fact table
4. `not_null_fct_customers_id` - Verify customer IDs are not null in fact table
5. `not_null_fct_customers_order_amount` - Verify order amounts are not null

All tests are defined in `dbt_project/models/schema.yml`.

## 📈 Evidence Dashboard

The Evidence dashboard includes:

### Pages

- **customers.md**: Main customer dashboard

### Components

1. **Customer Statistics Table**
    - Displays all customers with their details
    - Sortable columns
    - Download capability

2. **Customer Segmentation Chart**
    - Bar chart showing distribution across segments
    - Displays average order amounts

3. **Order Amount Distribution**
    - Line chart showing individual customer amounts
    - Ordered by amount descending

### Queries

The dashboard uses three SQL queries:

- `customers_summary`: All customer details
- `customer_segments`: Segment aggregations
- `order_distribution`: Individual customer amounts

## 🔧 Configuration Files

### dbt Configuration (`.dbt/profiles.yml`)

```yaml
dbt_poc:
    target: dev
    outputs:
        dev:
            type: duckdb
            path: "dbt.duckdb"
            schema: "main"
            threads: 4
```

### Evidence Configuration (`evidence/evidence.yml`)

```yaml
title: DuckDB + dbt POC Dashboard
description: Dashboard showcasing the integration of DuckDB, dbt, and Evidence.dev
```

### DuckDB Source (`evidence/sources/duckdb.source.yml`)

```yaml
type: duckdb
path: ../dbt.duckdb
```

## 📚 Common Commands

### dbt Commands

```bash
# Build all models
dbt run

# Run all tests
dbt test

# Build and test
dbt run --select stg_customers

# View documentation
dbt docs generate
dbt docs serve

# Clean compiled artifacts
dbt clean
```

### Evidence Commands

```bash
# Start development server
evidence

# Build for production
evidence build

# Preview built site
evidence preview
```

### Python Validation

```bash
# Run full validation
python validate_poc.py
```

## 🔍 Troubleshooting

### Issue: `dbt_poc' profile not found`

**Solution**: Ensure `DBT_PROFILES_DIR` is set correctly:

```bash
export DBT_PROFILES_DIR=.dbt
```

### Issue: DuckDB file not found

**Solution**: Run `dbt run` first to create the database:

```bash
cd dbt_project && dbt run && cd ..
```

### Issue: Evidence can't connect to DuckDB

**Solution**: Verify the path in `evidence/sources/duckdb.source.yml` is correct:

```yaml
path: ../dbt.duckdb # relative to evidence/ directory
```

### Issue: Port 3000 already in use

**Solution**: Use a different port with Evidence:

```bash
evidence --port 3001
```

## 📊 Sample Output

After running `python validate_poc.py`:

```
✅ Successfully connected to dbt.duckdb

📊 Available tables/views:
  - fct_customers
  - raw_customers
  - stg_customers

📈 Customer Metrics (fct_customers table):
ID  Name            Email                     Amount     Segment
6   Frank Miller    frank@example.com         $3200.50   High Value
8   Henry Davis     henry@example.com         $2500.75   High Value
3   Charlie Brown   charlie@example.com       $2150.00   High Value
4   Diana Prince    diana@example.com         $1875.25   Medium Value
1   Alice Johnson   alice@example.com         $1200.50   Medium Value

💰 Customer Segmentation Summary:
Segment         Count    Avg Amount   Total Amount
High Value      3        $2617.08     $7851.25
Medium Value    3        $1391.92     $4175.75
Low Value       2        $725.38      $1450.75
```

## 🎓 Learning Resources

- **DuckDB**: https://duckdb.org/docs/
- **dbt**: https://docs.getdbt.com/
- **Evidence**: https://docs.evidence.dev/
- **dbt-duckdb**: https://github.com/dbt-labs/dbt-duckdb

## ✅ Acceptance Criteria

- ✅ `dbt run` executes successfully without errors
- ✅ `dbt test` passes all 5 data quality tests
- ✅ Evidence.dev dashboard displays customer data with charts
- ✅ Complete DuckDB → dbt → Evidence chain validated

## 📝 Notes

- The project uses a simple SQL-based seed for demo data instead of traditional CSV loading
- All data is stored in a single `dbt.duckdb` file for portability
- The Evidence dashboard connects to DuckDB using the `@evidence-dev/datasource-duckdb` plugin
- The project is configured for development mode; production deployments would require additional security and scaling considerations

## 🤝 Next Steps

For enhancing this POC:

1. Add more complex dbt models with joins and aggregations
2. Implement incremental models for larger datasets
3. Add custom dbt tests and macros
4. Create multiple Evidence pages with different metrics
5. Integrate with a Git repository for version control
6. Set up CI/CD pipeline for automated testing and deployment

---

**Created**: April 14, 2026  
**Version**: 1.0.0  
**Status**: ✅ Complete and Validated
