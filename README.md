# Housing Association Compliance Demo DB

## Overview

This repository contains a PostgreSQL demo db designed to support the structured-data side of the housing association compliance bid solution. The goal is to provide realistic synthetic data for testing AI-powered discovery across structured and unstructured sources.

This database models:

- Properties
- Tenants
- Contractors
- Repair records
- FOI requests

> **Note:** This database is intended to be used alongside SharePoint-based unstructured data for the AI Foundry discovery use case.

---

## Purpose

This repo provides a small but realistic structured dataset that can be queried and explored as part of a housing association compliance / tenant information request use case. All data is synthetic and intended for **demo, prototype, and bid-support purposes only**.

The main idea is to simulate a scenario where a housing association needs to retrieve information linked to:

- A property
- A tenant
- Maintenance or repair history
- Contractor involvement
- FOI or tenant information requests

---

## Repository Structure

```
housing-association-compliance-db/
├── .gitignore
├── README.md
├── requirements.txt
├── sql/
│   ├── 001_create_tables.sql
│   ├── 002_seed_data.sql
│   └── 003_sample_queries.sql
├── scripts/
│   └── generate_seed_data.py
└── docs/
    └── data_model.md
```

---

## File Reference

### Root Files

| File | Description |
|------|-------------|
| `README.md` | Main documentation for setup and usage |
| `requirements.txt` | Python dependencies for the synthetic data generator |
| `.gitignore` | Prevents unnecessary files (e.g. `.venv`, IDE configs) from being committed |

### SQL Files

| File | Description |
|------|-------------|
| `sql/001_create_tables.sql` | Creates all database tables and relationships |
| `sql/002_seed_data.sql` | Inserts the base dataset into the database |
| `sql/003_sample_queries.sql` | Contains example queries to explore and validate the dataset |

### Scripts

**`scripts/generate_seed_data.py`** — Generates synthetic SQL `INSERT` statements.

- Does not connect to PostgreSQL directly
- Prints SQL output to the terminal
- Can be used to generate larger datasets

### Documentation

**`docs/data_model.md`** — Detailed description of entities and relationships.

---

## Data Model

### Tables

- `properties`
- `tenants`
- `contractors`
- `repair_records`
- `foi_requests`

### Relationships

| Relationship                    | Type |
|---------------------------------|---|
| One property > tenants          | One-to-many |
| One property > repair records   | One-to-many |
| One contractor > repair records | One-to-many |
| One tenant > FOI requests       | One-to-many |
| One property > FOI requests     | One-to-many |

---

## Prerequisites

Ensure the following are installed before proceeding:

- Python 3
- PostgreSQL
- `psql` CLI
- Git

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <the-repo-ssh>
cd housing-association-compliance-db
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Creates an isolated Python environment to avoid conflicts with global packages. Your terminal prompt will show `(.venv)` when active.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Installs required libraries (e.g. `Faker`). All packages should install with no errors.

### 4. Create the PostgreSQL Database

```bash
psql postgres
CREATE DATABASE housing_demo;
\q
```

Opens the PostgreSQL CLI and creates a new database. You should see a `CREATE DATABASE` confirmation.

### 5. Create Tables

```bash
psql -d housing_demo -f sql/001_create_tables.sql
```

Creates all tables. Expected output: multiple `CREATE TABLE` confirmations.

### 6. Load Seed Data

```bash
psql -d housing_demo -f sql/002_seed_data.sql
```

Inserts the initial dataset. Expected output: multiple `INSERT` confirmations.

### 7. Run Sample Queries

```bash
psql -d housing_demo -f sql/003_sample_queries.sql
```

Runs validation queries and prints tables of data to the terminal.

---

## Using the Synthetic Data Generator

### Run the Script

```bash
python3 scripts/generate_seed_data.py
```

Generates SQL `INSERT` statements and displays them in the terminal.

### Save Output to a File

```bash
python3 scripts/generate_seed_data.py > sql/004_generated_seed.sql
```

### Load Generated Data into PostgreSQL

```bash
psql -d housing_demo -f sql/004_generated_seed.sql
```

---

## Example Query

```sql
SELECT p.address_line_1, t.first_name, t.last_name
FROM properties p
JOIN tenants t ON p.property_id = t.property_id;
```

---

## What You Should Be Able to Do

After completing setup, you should be able to:

- Query properties and tenants
- View repair history per property
- Link contractors to repairs
- Retrieve FOI requests linked to tenants and properties

---

## Notes

- All data is **synthetic** — no real personal data is used
- Designed for **demos, testing, and prototyping only**
