# Housing Association Compliance Demo Database

## Overview

This repository contains a PostgreSQL demo database designed to support the structured-data side of the housing association compliance bid solution.

The goal is to provide realistic synthetic data for testing AI-powered discovery across structured and unstructured sources.

This database models:

- properties
- tenants
- contractors
- repair records
- FOI requests

It is intended to be used alongside SharePoint-based unstructured data for the AI Foundry discovery use case.

---

## Repository Structure

```bash
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