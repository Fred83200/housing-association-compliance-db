# Data Model

## Purpose

This document describes the PostgreSQL data model used for the structured-data side of the housing association compliance discovery solution.

The database is designed to provide synthetic but realistic records that can be queried directly and later connected to AI-powered discovery tooling such as Microsoft AI Foundry.

The model focuses on the minimum set of entities needed to demonstrate structured discovery across housing, tenant, contractor, repair, and FOI-related information.

---

## Entity Overview

The database contains five tables:

- `properties`
- `tenants`
- `contractors`
- `repair_records`
- `foi_requests`

Each table has been designed to support a realistic discovery scenario in which information requests can be traced across related records.

---

## 1. Properties

The `properties` table stores information about housing association properties.

### Key fields

- `property_id` - primary key
- `uprn` - unique property reference
- `address_line_1`
- `address_line_2`
- `city`
- `postcode`
- `property_type`
- `bedrooms`
- `build_year`
- `compliance_status`
- `last_inspection_date`

### Purpose

This table provides the core asset or location that other records relate to.

---

## 2. Tenants

The `tenants` table stores tenant records linked to properties.

### Key fields

- `tenant_id` - primary key
- `property_id` - foreign key to `properties`
- `first_name`
- `last_name`
- `date_of_birth`
- `email`
- `phone`
- `tenancy_start_date`
- `tenancy_end_date`
- `is_primary_tenant`

### Purpose

This table identifies who is associated with a property and who may raise an FOI or information request.

---

## 3. Contractors

The `contractors` table stores external contractor organisations.

### Key fields

- `contractor_id` - primary key
- `contractor_name`
- `specialism`
- `email`
- `phone`
- `active`

### Purpose

This table supports linking repairs and maintenance activity to the organisation that carried out the work.

---

## 4. Repair Records

The `repair_records` table stores maintenance, inspection, and repair activity for properties.

### Key fields

- `repair_id` - primary key
- `property_id` - foreign key to `properties`
- `contractor_id` - foreign key to `contractors`
- `reported_date`
- `scheduled_date`
- `completed_date`
- `repair_category`
- `description`
- `status`
- `cost`
- `notes`

### Purpose

This table provides the maintenance and compliance history of a property, which is a key part of the information request use case.

---

## 5. FOI Requests

The `foi_requests` table stores tenant information requests and request lifecycle details.

### Key fields

- `foi_request_id` - primary key
- `tenant_id` - foreign key to `tenants`
- `property_id` - foreign key to `properties`
- `request_reference`
- `request_date`
- `due_date`
- `request_type`
- `request_summary`
- `status`
- `assigned_to`
- `response_date`

### Purpose

This table represents the central business process being supported in the demo: the tracking and fulfilment of tenant information requests.

---

## Relationships

The tables are related as follows:

- One property can have many tenants.
- One property can have many repair records.
- One contractor can have many repair records.
- One tenant can have many FOI requests.
- One property can have many FOI requests.

---

## Relationship Summary

### `properties` -> `tenants`
- Relationship: one-to-many
- Key: `tenants.property_id` references `properties.property_id`

### `properties` -> `repair_records`
- Relationship: one-to-many
- Key: `repair_records.property_id` references `properties.property_id`

### `contractors` -> `repair_records`
- Relationship: one-to-many
- Key: `repair_records.contractor_id` references `contractors.contractor_id`

### `tenants` -> `foi_requests`
- Relationship: one-to-many
- Key: `foi_requests.tenant_id` references `tenants.tenant_id`

### `properties` -> `foi_requests`
- Relationship: one-to-many
- Key: `foi_requests.property_id` references `properties.property_id`

---

## Why This Model Works for the Demo

This model is intentionally lightweight but realistic enough to support:

- cross-table discovery
- linked search across housing and tenant records
- maintenance and compliance history retrieval
- tenant information request tracking
- structured-data testing alongside SharePoint or other document sources

It gives our team a credible structured source for demonstrating discovery without over-engineering the DB.

---

## Future Enhancements

If the demo needs to expand later, we could add tables like:

- `documents`
- `inspections`
- `complaints`
- `tenancy_correspondence`
- `compliance_certificates`

These are not required for the initial MVP but could enrich the discovery use case further.