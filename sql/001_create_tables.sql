CREATE TABLE properties (
    property_id SERIAL PRIMARY KEY,
    uprn VARCHAR(50) UNIQUE NOT NULL,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    postcode VARCHAR(20) NOT NULL,
    property_type VARCHAR(50),
    bedrooms INTEGER,
    build_year INTEGER,
    compliance_status VARCHAR(50),
    last_inspection_date DATE
);

CREATE TABLE tenants (
    tenant_id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    email VARCHAR(255),
    phone VARCHAR(50),
    tenancy_start_date DATE NOT NULL,
    tenancy_end_date DATE,
    is_primary_tenant BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_tenants_property
        FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE
);

CREATE TABLE contractors (
    contractor_id SERIAL PRIMARY KEY,
    contractor_name VARCHAR(255) NOT NULL,
    specialism VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE repair_records (
    repair_id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    contractor_id INTEGER,
    reported_date DATE NOT NULL,
    scheduled_date DATE,
    completed_date DATE,
    repair_category VARCHAR(100),
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    cost NUMERIC(10,2),
    notes TEXT,
    CONSTRAINT fk_repairs_property
        FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_repairs_contractor
        FOREIGN KEY (contractor_id)
        REFERENCES contractors(contractor_id)
        ON DELETE SET NULL
);

CREATE TABLE foi_requests (
    foi_request_id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    request_reference VARCHAR(50) UNIQUE NOT NULL,
    request_date DATE NOT NULL,
    due_date DATE NOT NULL,
    request_type VARCHAR(100),
    request_summary TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(255),
    response_date DATE,
    CONSTRAINT fk_foi_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_foi_property
        FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE
);