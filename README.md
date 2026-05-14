# Housing Association Compliance Demo DB

>All data is synthetic and intended for demo, prototype, and bid-support purposes only

---

## Overview

A PostgreSQL demo database designed to support the structured data side of a housing association compliance bid solution. It provides realistic synthetic data for testing AI-powered discovery across structured and unstructured sources.

This project has evolved beyond a simple database — it now includes a **full discovery layer simulating Azure AI Foundry**, comprising a PostgreSQL database, optimised queries, a FastAPI layer, a keyword-based query router, and a lightweight chat UI.

> This setup mirrors how an AI-powered discovery system would behave **without requiring Azure or paid services**.

---

## What This Models

- Properties
- Tenants
- Contractors
- Repair records
- FOI requests

This database is intended to be used alongside SharePoint-based unstructured data for the AI Foundry discovery use case

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
│   ├── 004_generated_seed.sql      full synthetic dataset (recommended)
│   ├── 005_create_indexes.sql
│   ├── 006_create_views.sql
│   └── 007_create_readonly_user.sql
├── scripts/
│   └── generate_seed_data.py       regenerates 004_generated_seed.sql
├── app/
│   ├── main.py
│   ├── database.py
│   ├── document_retrieval_service.py
│   ├── discovery_service.py
│   ├── query_router.py
│   └── static/
│       └── index.html
├── documents/
│   ├── property_1_boiler_report.txt
│   ├── property_1_damp_mould_notes.txt
│   ├── property_2_electrical_inspection.txt
│   ├── property_4_fire_safety_report.txt
└── docs/
    └── data_model.md
```

---

## Data Model

### Tables

| Table | Key Fields |
|---|---|
| `properties` | `property_id`, `uprn`, `address_line_1`, `city`, `postcode`, `property_type`, `bedrooms`, `build_year`, `compliance_status`, `last_inspection_date` |
| `tenants` | `tenant_id`, `property_id`, `first_name`, `last_name`, `email`, `phone`, `tenancy_start_date`, `tenancy_end_date`, `is_primary_tenant` |
| `contractors` | `contractor_id`, `contractor_name`, `specialism`, `email`, `phone`, `active` |
| `repair_records` | `repair_id`, `property_id`, `contractor_id`, `repair_category`, `description`, `status`, `reported_date`, `scheduled_date`, `completed_date`, `cost` |
| `foi_requests` | `foi_request_id`, `tenant_id`, `property_id`, `request_reference`, `request_type`, `request_summary`, `status`, `due_date`, `response_date`, `assigned_to` |

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
git clone <repo-ssh>
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

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_NAME=housing_compliance_demo
DATABASE_USER=your_postgres_username
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

> **Important:** `database.py` loads these values via `python-dotenv`. Without a `.env` file the default user is `fred`, which will cause the API to fail to connect unless your local PostgreSQL user happens to be named `fred`. No password field is configured, so your PostgreSQL user must be able to connect without a password (e.g. via `trust` authentication in `pg_hba.conf`).

### 5. Create the database

```bash
psql postgres
CREATE DATABASE housing_compliance_demo;
\q
```

### 6. Run database setup (in order)

```bash
psql -d housing_compliance_demo -f sql/000_drop_tables.sql
psql -d housing_compliance_demo -f sql/001_create_tables.sql
psql -d housing_compliance_demo -f sql/004_generated_seed.sql
psql -d housing_compliance_demo -f sql/005_create_indexes.sql
psql -d housing_compliance_demo -f sql/006_create_views.sql
```

**Alternative — base dataset only:**

```bash
psql -d housing_compliance_demo -f sql/000_drop_tables.sql
psql -d housing_compliance_demo -f sql/001_create_tables.sql
psql -d housing_compliance_demo -f sql/002_seed_data.sql
psql -d housing_compliance_demo -f sql/005_create_indexes.sql
psql -d housing_compliance_demo -f sql/006_create_views.sql
```

### 7. Validate data loaded

```bash
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM properties;"
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM tenants;"
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM repair_records;"
psql -d housing_compliance_demo -c "SELECT COUNT(*) FROM foi_requests;"
```

> All counts should be non zero

---

## Synthetic Data Generator

To regenerate the seed data:

```bash
python3 scripts/generate_seed_data.py > sql/004_generated_seed.sql
```

Then reload the database:

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

Six precomputed views used by the API:

| View | Description |
|---|---|
| `vw_property_overview` | Per-property summary with tenant, repair, and FOI counts |
| `vw_property_repair_history` | Repair records joined with contractor details |
| `vw_property_foi_requests` | FOI requests joined with tenant and property details |
| `vw_non_compliant_properties` | Properties with `compliance_status = 'Non-Compliant'` |
| `vw_overdue_inspections` | Properties where `last_inspection_date` is over 365 days ago |
| `vw_overdue_foi_requests` | FOI requests past `due_date` with no `response_date` |

### Read-only user — `007_create_readonly_user.sql`

Creates a restricted database user to simulate production level access control

---

## Discovery API (Simulated Azure AI Foundry)

### Start the API

```bash
uvicorn app.main:app --reload
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `POST` | `/chat` | Submit a question, returns matched data |
| `GET` | `/properties/{property_id}/case-file` | Full case file for a property (overview, repairs, FOI) |
| `GET` | `/docs` | Swagger UI / interactive API documentation |

### How the query router works

> **Important:** The query router uses **keyword matching**, not true natural language understanding. Questions must contain specific trigger words to be routed correctly. Rephrasing a question can cause it to return no results.

The routing rules are:

| Trigger keywords in question | Intent |
|---|---|
| `non-compliant` or `non compliant` | Non-compliant properties |
| `compliant` (without "non") | Compliant properties |
| `overdue` + `inspection` | Overdue inspections |
| `inspected after` | Properties inspected after a given date |
| `properties in` | Properties filtered by city |
| `overdue` + `foi` or `request` | Overdue FOI requests |
| `property`, `postcode`, or `uprn` | Property lookup by address, postcode, or UPRN |

If no keywords match, the router returns an `"unknown"` intent with a suggestion to rephrase.

> **Result limits:** Most queries return a maximum of **20 rows**. Property lookups return a maximum of **10 rows**.

> **Overdue inspection logic:** A property is considered overdue for inspection if its `last_inspection_date` is more than **365 days ago** — there is no separate scheduled due date field.

### Supported questions — exact working examples

**Compliance**
```
Show me compliant properties
Show me non-compliant properties
```

**Inspections**
```
Show me overdue inspections
Show me properties inspected after 2024-01-01
```

**FOI**
```
Show me overdue FOI requests
Show me overdue requests
```

**Location**
```
Show me properties in London
Show me properties in Manchester
```

**Lookup**
```
Find property SW1A 1AA
Find postcode SW1A 1AA
Find UPRN UPRNX00001
```

**Documents (RAG)**
```
Show me documents about boiler repair
Find reports about fire safety
Show me documents about damp and mould
```

**Combined (Structured + Documents)**
```
Show me everything for property 1
```

### Example SQL query

```sql
SELECT p.address_line_1, t.first_name, t.last_name
FROM properties p
JOIN tenants t ON p.property_id = t.property_id;
```

---

## Unstructured Data — RAG Simulation (Local SharePoint Equivalent)

This project includes a lightweight Retrieval Augmented Generation (RAG) simulation to demonstrate how unstructured data (e.g. SharePoint documents) can be integrated with structured database queries.

### Why this exists

In a real Azure AI Foundry setup:

- Documents would live in SharePoint / Blob Storage
- They would be indexed using Azure AI Search
- Queries would retrieve relevant documents dynamically

> This project simulates that behaviour locally and for free.

### How It Works

The RAG pipeline is implemented in:

```
app/document_retrieval_service.py
```

It follows a simplified version of a real world retrieval flow:

**Step 1 — User Question**

Example:
```
Show me documents about boiler repair
```

**Step 2 — Keyword Extraction**

The system removes:
- Stop words (`show`, `me`, `about`, etc.)
- Generic words (`report`, `document`, etc.)

Result:
```
["boiler", "repair"]
```

**Step 3 — Document Scanning**

All files in:
```
/documents/*.txt
```
are read and analysed. Each document contains structured metadata such as:
- Property ID
- Document Type
- Category
- Keywords

**Step 4 — Scoring**

Each document is scored based on keyword matches:

| Keyword Type | Weight |
|---|---|
| Important domain keywords (`boiler`, `fire`, `damp`) | High (5+) |
| Standard matches | Medium (2–3) |

> Only documents above a relevance threshold are returned

**Step 5 — Ranked Results**

The API returns:
- File name
- Relevance score
- Content preview

### Example RAG Queries (Working)

These are fully supported and tested queries:

**Boiler**
```
Show me documents about boiler repair
```
Returns: Boiler repair report only

**Fire Safety**
```
Find reports about fire safety
```
Returns: Fire safety inspection report

**Damp & Mould**
```
Show me documents about damp and mould
```
Returns: Damp & mould investigation notes

### Property Case File + Documents (Hybrid Query)

The system also supports combined structured + unstructured retrieval:

```
Show me everything for property 1
```

Returns:
- Property overview (DB)
- Repairs (DB)
- FOI requests (DB)
- Documents (RAG)

This simulates a real AI Foundry "case file" retrieval scenario

### Design Decisions

| Decision | Reason |
|---|---|
| Local `.txt` documents | No dependency on SharePoint |
| Keyword scoring | Deterministic and controllable |
| No embeddings | Avoid cost and complexity |
| Weighted keywords | Improve relevance for domain terms |
| Threshold filtering | Avoid noisy results |

### Limitations (Expected for PoC)

- No semantic understanding (keyword based only)
- No embeddings / vector search
- No document chunking
- No cross document summarisation

> This is intentional the goal is to prove the architecture, not the ML

### How This Maps to Azure AI Foundry

| This Project | Real Azure Equivalent |
|---|---|
| `/documents` folder | SharePoint / Blob Storage |
| Keyword scoring | Vector search / embeddings |
| `document_retrieval_service.py` | Retrieval pipeline |
| Query router | Orchestration layer |
| `/chat` endpoint | Copilot / AI agent |



## Design Principles

| Principle | Detail                                        |
|---|-----------------------------------------------|
| No external AI dependency | Cost-free, runs locally                       |
| Controlled SQL execution | No arbitrary query injection                  |
| Precomputed views | Fast, predictable responses                   |
| Indexed queries | No full table scans                           |
| Clean separation of concerns | DB = storage - API = logic - UI = interaction |

### Expected performance

- API responds in 1–3 seconds
- Queries return structured results
- Chat UI displays data immediately

---

## Notes

- All data is entirely synthetic
- No real personal data is used at any point
- This project is designed for **demo, testing, and prototyping only**

---

## Azure Deployment

The app can run against live Azure services instead of local equivalents. Copy `.env.example` to `.env` and populate the non-secret values:

```bash
cp .env.example .env
```

Get values from the Terraform outputs (run from `stairs-response-agent/terraform`):

```bash
terraform output foundry_endpoint   # → AZURE_OPENAI_ENDPOINT
terraform output postgresql_fqdn    # → DATABASE_HOST
terraform output search_endpoint    # → SEARCH_ENDPOINT
terraform output key_vault_uri      # → AZURE_KEYVAULT_URI
```

**Secrets are fetched from Key Vault at runtime** — no need to set `DATABASE_PASSWORD`, `AZURE_OPENAI_API_KEY`, or `SEARCH_API_KEY` in `.env` when `AZURE_KEYVAULT_URI` is set. The app uses `DefaultAzureCredential` (`az login` locally, managed identity in the Container App) to read `postgresql-password`, `openai-api-key`, and `search-api-key` from Key Vault.

For local dev without Key Vault access, set the fallback env vars directly in `.env` (see commented lines in `.env.example`).

To deploy as a container to Azure Container Apps, see `stairs-response-agent/README.md`.
