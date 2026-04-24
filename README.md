# Housing Association Compliance Demo DB

>All data is synthetic and intended for demo, prototype, and bid-support purposes only

---

## Overview

A PostgreSQL demo database designed to support the structured data side of a housing association compliance bid solution. It provides realistic synthetic data for testing AI-powered discovery across structured and unstructured sources.

This project has evolved beyond a simple database — it now includes a **full discovery layer simulating Azure AI Foundry**, comprising a PostgreSQL database, optimised queries, a FastAPI layer, a natural language query router, and a lightweight chat UI.

> This setup mirrors how an AI-powered discovery system would behave **without requiring Azure or paid services**.

---

## What This Models

- Properties
- Tenants
- Contractors
- Repair records
- FOI requests

This database is intended to be used alongside SharePoint-based unstructured data for the AI Foundry discovery use case.

---

## Repository Structure

```
housing-association-compliance-db/
├── .gitignore
├── README.md
├── requirements.txt
├── sql/
│   ├── 000_drop_tables.sql
│   ├── 001_create_tables.sql
│   ├── 002_seed_data.sql
│   ├── 003_sample_queries.sql
│   ├── 004_generated_seed.sql
│   ├── 005_create_indexes.sql
│   ├── 006_create_views.sql
│   └── 007_create_readonly_user.sql
├── scripts/
│   └── generate_seed_data.py
├── app/
│   ├── main.py
│   ├── database.py
│   ├── discovery_service.py
│   ├── query_router.py
│   └── static/
│       └── index.html
└── docs/
    └── data_model.md
```

---

## Data Model

### Tables

| Table | Description |
|---|---|
| `properties` | Housing association properties |
| `tenants` | Tenants linked to properties |
| `contractors` | Contractors involved in repairs |
| `repair_records` | Maintenance and repair history |
| `foi_requests` | Freedom of Information requests |

### Relationships

| Relationship | Type |
|---|---|
| One property → tenants | One-to-many |
| One property → repair records | One-to-many |
| One contractor → repairs | One-to-many |
| One tenant → FOI requests | One-to-many |
| One property → FOI requests | One-to-many |

---

## Prerequisites

Ensure the following are installed before setup:

- Python 3
- PostgreSQL
- `psql` CLI
- Git

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-ssh>
cd housing-association-compliance-db
```

### 2. Create Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> The terminal prompt should now show `(.venv)`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the database

```bash
psql postgres
CREATE DATABASE housing_compliance_demo;
\q
```

### 5. Run database setup (in order)

```bash
psql -d housing_compliance_demo -f sql/000_drop_tables.sql
psql -d housing_compliance_demo -f sql/001_create_tables.sql
psql -d housing_compliance_demo -f sql/004_generated_seed.sql
psql -d housing_compliance_demo -f sql/005_create_indexes.sql
psql -d housing_compliance_demo -f sql/006_create_views.sql
```

**Alternative — base dataset only:**

```bash
psql -d housing_compliance_demo -f sql/002_seed_data.sql
```

### 6. Validate data loaded

```bash
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM properties;"
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM tenants;"
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM repair_records;"
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM foi_requests;"
```

> All counts should be non zero

---

## Synthetic Data Generator

### Generate a new dataset

```bash
python3 scripts/generate_seed_data.py > sql/004_generated_seed.sql
```

### Reload the database with new data

```bash
psql -d housing_compliance_demo -f sql/000_drop_tables.sql
psql -d housing_compliance_demo -f sql/001_create_tables.sql
psql -d housing_compliance_demo -f sql/004_generated_seed.sql
```

---

## Database Optimisation

### Indexes — `005_create_indexes.sql`

Improves query performance for:

- Compliance filtering
- City search
- FOI lookups
- Inspection queries

### Views — `006_create_views.sql`

Precomputed datasets used by the API for fast responses:

| View | Description |
|---|---|
| `vw_non_compliant_properties` | Properties failing compliance checks |
| `vw_overdue_inspections` | Properties with overdue inspections |
| `vw_overdue_foi_requests` | FOI requests past their response deadline |

### Read-only user — `007_create_readonly_user.sql`

Creates a restricted database user to simulate production level access control

---

## Discovery API (Simulated Azure AI Foundry)

### Start the API

```bash
uvicorn app.main:app --reload
```

### Access points

| Interface | URL |
|---|---|
| Chat UI | http://127.0.0.1:8000 |
| Swagger / API docs | http://127.0.0.1:8000/docs |

### How it works

1. User submits a question via the chat UI
2. API receives it at `/chat`
3. `query_router.py` detects the intent
4. `discovery_service.py` executes the appropriate SQL
5. Results are returned as JSON
6. UI renders the response

### Supported query types

**Compliance**
- Show me compliant properties
- Show me non-compliant properties

**Inspections**
- Show me overdue inspections
- Show me properties inspected after 2025-07-01

**FOI**
- Show me overdue FOI requests

**Location**
- Show me properties in London

**Lookup**
- Find property SW1A 1AA
- Find UPRN UPRNX00001

### Example SQL query

```sql
SELECT p.address_line_1, t.first_name, t.last_name
FROM properties p
JOIN tenants t ON p.property_id = t.property_id;
```

---

## Design Principles

| Principle | Detail                                       |
|---|----------------------------------------------|
| No external AI dependency | Cost free, runs locally                      |
| Controlled SQL execution | No arbitrary query injection                 |
| Precomputed views | Fast predictable responses                   |
| Indexed queries | No full table scans                          |
| Clean separation of concerns | DB = storage · API = logic · UI = interaction |

### Expected performance

- API responds in 1-3 seconds
- Queries return structured results
- Chat UI displays data immediately

---

## Future Improvements

- [ ] Integrate a real LLM (Azure OpenAI or OpenAI API)
- [ ] Add document retrieval via SharePoint / RAG pipeline
- [ ] Add a caching layer
- [ ] Expand natural language query understanding
- [ ] Build dashboards for common compliance queries

---

## Notes

- All data is entirely synthetic
- No real personal data is used at any point
- This project is designed for **demo, testing, and prototyping only**
