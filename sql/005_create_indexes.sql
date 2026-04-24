CREATE INDEX IF NOT EXISTS idx_properties_postcode
ON properties (postcode);

CREATE INDEX IF NOT EXISTS idx_properties_compliance_status
ON properties (compliance_status);

CREATE INDEX IF NOT EXISTS idx_tenants_property_id
ON tenants (property_id);

CREATE INDEX IF NOT EXISTS idx_repair_records_property_id
ON repair_records (property_id);

CREATE INDEX IF NOT EXISTS idx_repair_records_contractor_id
ON repair_records (contractor_id);

CREATE INDEX IF NOT EXISTS idx_foi_requests_property_id
ON foi_requests (property_id);

CREATE INDEX IF NOT EXISTS idx_foi_requests_tenant_id
ON foi_requests (tenant_id);

CREATE INDEX IF NOT EXISTS idx_foi_requests_status
ON foi_requests (status);

CREATE INDEX IF NOT EXISTS idx_foi_requests_due_date
ON foi_requests (due_date);