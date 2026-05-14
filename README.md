# Housing Association Compliance Demo

> All data is synthetic and intended for demo, prototype, and bid-support purposes only.

---

## Overview

A FastAPI application providing an AI-powered compliance discovery system for housing associations. It queries structured data from PostgreSQL and unstructured documents via Azure AI Search, using GPT-4o through Azure AI Foundry for intent classification and response generation.

---

## Architecture

```text
User → FastAPI (/chat)
         ├── query_router.py  (intent classification via GPT-4o)
         │     ├── discovery_service.py  → PostgreSQL (structured data)
         │     └── document_retrieval_service.py  → Azure AI Search (hybrid)
         └── vector_store.py  → Azure AI Search (semantic / vector)
```

**Azure services used:**

| Service | Purpose |
| --- | --- |
| Azure AI Services (AIServices) | GPT-4o chat + text-embedding-3-small embeddings |
| Azure AI Foundry Hub + Project | Orchestration layer |
| Azure AI Search | Hybrid keyword + vector document search |
| Azure PostgreSQL Flexible Server | Structured compliance data |
| Azure Blob Storage | Document storage (indexing source) |
| Azure Key Vault | Secrets management |
| Azure Container Registry | Docker image storage |
| Azure Container Apps | API hosting (serverless containers) |

---

## Repository Structure

```text
housing-association-compliance-db/
├── app/
│   ├── main.py                        FastAPI app + endpoints
│   ├── database.py                    PostgreSQL connection (SSL-aware)
│   ├── llm_client.py                  Azure OpenAI chat completions
│   ├── embedding_service.py           Azure OpenAI embeddings
│   ├── vector_store.py                Azure AI Search index + semantic search
│   ├── document_retrieval_service.py  Azure AI Search hybrid search
│   ├── query_router.py                Intent classification + routing
│   ├── discovery_service.py           SQL query functions (13 queries, 6 views)
│   ├── configs.py                     Intent → handler class mapping
│   ├── ai_question_clarifiers/        11 intent-specific LLM handlers
│   └── static/                        Chat UI (index.html)
├── documents/
│   ├── structured/                    Structured .txt documents
│   └── unstructured/                  Unstructured .txt documents
├── sql/
│   ├── 001_create_tables.sql
│   ├── 004_generated_seed.sql         52K-row synthetic dataset
│   ├── 005_create_indexes.sql
│   └── 006_create_views.sql           6 precomputed views
├── scripts/
│   └── generate_seed_data.py
├── Dockerfile
├── .env.example
└── requirements.txt
```

---

## Data Model

### Tables

| Table | Key Fields |
| --- | --- |
| `properties` | `property_id`, `uprn`, `address_line_1`, `city`, `postcode`, `compliance_status`, `last_inspection_date` |
| `tenants` | `tenant_id`, `property_id`, `first_name`, `last_name`, `tenancy_start_date` |
| `contractors` | `contractor_id`, `contractor_name`, `specialism` |
| `repair_records` | `repair_id`, `property_id`, `contractor_id`, `repair_category`, `status`, `cost` |
| `foi_requests` | `foi_request_id`, `tenant_id`, `property_id`, `request_reference`, `status`, `due_date` |

### Views

| View | Description |
| --- | --- |
| `vw_property_overview` | Per-property summary with tenant, repair, and FOI counts |
| `vw_property_repair_history` | Repairs joined with contractor details |
| `vw_property_foi_requests` | FOI requests joined with tenant and property |
| `vw_non_compliant_properties` | Properties with `compliance_status = 'Non-Compliant'` |
| `vw_overdue_inspections` | Properties without inspection in the last 365 days |
| `vw_overdue_foi_requests` | FOI requests past `due_date` with no `response_date` |

---

## Azure Deployment

### Prerequisites

- Azure infrastructure provisioned via `stairs-response-agent/terraform` (see that repo's README)
- Terraform outputs available: `foundry_endpoint`, `postgresql_fqdn`, `search_endpoint`

### 1. Configure environment variables

Copy `.env.example` to `.env` and fill in values from the Terraform outputs and Key Vault:

```bash
cp .env.example .env
```

Get the values:

```bash
cd ../stairs-response-agent/terraform
terraform output foundry_endpoint    # → AZURE_OPENAI_ENDPOINT
terraform output postgresql_fqdn     # → DATABASE_HOST
terraform output search_endpoint     # → SEARCH_ENDPOINT (from ai_search module output)
```

Retrieve secrets from Key Vault:

```bash
az keyvault secret show --vault-name kv-cmplianz-hack --name openai-api-key --query value -o tsv
az keyvault secret show --vault-name kv-cmplianz-hack --name search-api-key --query value -o tsv
```

Your `.env` should look like:

```env
DATABASE_NAME=housing_compliance_demo
DATABASE_USER=pgadmin
DATABASE_HOST=psql-cmplianz-hack.postgres.database.azure.com
DATABASE_PORT=5432
DATABASE_PASSWORD=<your-password>
DATABASE_SSL=require

AZURE_OPENAI_ENDPOINT=https://swedencentral.api.cognitive.microsoft.com/
AZURE_OPENAI_API_KEY=<from key vault>
AZURE_AI_DEPLOYMENT=gpt-4o
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small

SEARCH_ENDPOINT=https://srch-cmplianz-hack.search.windows.net
SEARCH_API_KEY=<from key vault>
```

### 2. Run the SQL schema against Azure PostgreSQL

```bash
PGPASSWORD=<your-password> psql \
  "host=psql-cmplianz-hack.postgres.database.azure.com \
   user=pgadmin \
   dbname=housing_compliance_demo \
   sslmode=require" \
  -f sql/001_create_tables.sql \
  -f sql/004_generated_seed.sql \
  -f sql/005_create_indexes.sql \
  -f sql/006_create_views.sql
```

Verify:

```bash
PGPASSWORD=<your-password> psql \
  "host=psql-cmplianz-hack.postgres.database.azure.com user=pgadmin dbname=housing_compliance_demo sslmode=require" \
  -c "SELECT COUNT(*) FROM properties;"
```

### 3. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run locally against Azure

```bash
uvicorn app.main:app --reload
```

On first startup, the app will:
1. Create the Azure AI Search index `housing-compliance-docs` (if it doesn't exist)
2. Embed all `.txt` files under `documents/` using `text-embedding-3-small`
3. Upload the chunks to Azure AI Search (skipped on subsequent starts if the index is non-empty)

### 5. Deploy to Azure Container Apps

The app is containerised and deployed via Azure Container Registry (ACR). Terraform provisions the ACR, Container App Environment, and Container App. All secrets are injected as Container App secrets (not plain env vars) by Terraform.

**Build and push the image:**

```bash
az acr build \
  --registry acrcmplianzhack \
  --image compliance-api:latest \
  .
```

This builds the `Dockerfile` remotely in Azure and pushes the image to ACR — no local Docker required.

**The Terraform apply (run from `stairs-response-agent/`) creates the Container App automatically pointing to this image.** If you rebuild the image after the initial deploy, update the running app with:

```bash
az containerapp update \
  --name app-cmplianz-hack \
  --resource-group rg-cmplianz-hack-uksouth \
  --image acrcmplianzhack.azurecr.io/compliance-api:latest
```

**Live URL:**

```
https://app-cmplianz-hack--w0xvovn.victoriousdesert-feee0ad1.uksouth.azurecontainerapps.io
```

---

## Local Development (no Azure)

> This mode uses a local PostgreSQL database. Azure AI Search and Azure OpenAI are still required for document search and LLM features.

### 1. Create a local PostgreSQL database

```bash
psql postgres -c "CREATE DATABASE housing_compliance_demo;"
psql -d housing_compliance_demo -f sql/001_create_tables.sql
psql -d housing_compliance_demo -f sql/004_generated_seed.sql
psql -d housing_compliance_demo -f sql/005_create_indexes.sql
psql -d housing_compliance_demo -f sql/006_create_views.sql
```

### 2. Configure `.env` for local PostgreSQL

```env
DATABASE_NAME=housing_compliance_demo
DATABASE_USER=<your-local-postgres-user>
DATABASE_HOST=localhost
DATABASE_PORT=5432
# No DATABASE_PASSWORD or DATABASE_SSL for local trust auth
```

Keep Azure vars (`AZURE_OPENAI_ENDPOINT`, `SEARCH_ENDPOINT`, etc.) as-is.

---

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Submit a question, returns intent + matched data |
| `GET` | `/stairs-requests` | All FOI / STAIRS requests |
| `GET` | `/dashboard-summary` | Portfolio-level compliance metrics |
| `GET` | `/properties-requiring-attention` | Properties needing action |
| `GET` | `/properties/{id}/case-file` | Full structured + document case file |
| `GET` | `/docs` | Swagger UI |

### Example questions

```
Show me non-compliant properties
Show me overdue inspections
Show me overdue FOI requests
Show me properties in London
Find postcode SW1A 1AA
Show me documents about boiler repair
Show me everything for property 1
```

---

## How document search works

On startup, `vector_store.py` creates an Azure AI Search index (`housing-compliance-docs`) and ingests all `.txt` files from `documents/` as 500-character overlapping chunks with `text-embedding-3-small` embeddings. Subsequent startups skip ingestion if the index is already populated.

Both `vector_store.py` (semantic search) and `document_retrieval_service.py` (hybrid keyword + semantic search) query the same index. The `/chat` endpoint uses both paths depending on the detected intent.

---

## Security notes

- Never commit `.env` — it is in `.gitignore`
- Database password, OpenAI API key, and Search API key are stored in Azure Key Vault and injected at runtime
- Azure PostgreSQL requires `sslmode=require` — enforced via `DATABASE_SSL=require`
- All SQL queries use parameterised statements (no injection risk)
