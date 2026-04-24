CREATE OR REPLACE VIEW vw_property_overview AS
SELECT
    p.property_id,
    p.uprn,
    p.address_line_1,
    p.address_line_2,
    p.city,
    p.postcode,
    p.property_type,
    p.bedrooms,
    p.compliance_status,
    p.last_inspection_date,
    COUNT(DISTINCT t.tenant_id) AS tenant_count,
    COUNT(DISTINCT r.repair_id) AS repair_count,
    COUNT(DISTINCT f.foi_request_id) AS foi_request_count
FROM properties p
LEFT JOIN tenants t
    ON p.property_id = t.property_id
LEFT JOIN repair_records r
    ON p.property_id = r.property_id
LEFT JOIN foi_requests f
    ON p.property_id = f.property_id
GROUP BY
    p.property_id,
    p.uprn,
    p.address_line_1,
    p.address_line_2,
    p.city,
    p.postcode,
    p.property_type,
    p.bedrooms,
    p.compliance_status,
    p.last_inspection_date;

CREATE OR REPLACE VIEW vw_property_repair_history AS
SELECT
    p.property_id,
    p.uprn,
    p.address_line_1,
    p.postcode,
    r.repair_id,
    r.repair_category,
    r.description,
    r.status,
    r.reported_date,
    r.scheduled_date,
    r.completed_date,
    c.contractor_name,
    c.specialism
FROM properties p
JOIN repair_records r
    ON p.property_id = r.property_id
LEFT JOIN contractors c
    ON r.contractor_id = c.contractor_id;

CREATE OR REPLACE VIEW vw_property_foi_requests AS
SELECT
    p.property_id,
    p.uprn,
    p.address_line_1,
    p.postcode,
    t.tenant_id,
    t.first_name,
    t.last_name,
    f.foi_request_id,
    f.request_reference,
    f.request_date,
    f.due_date,
    f.request_type,
    f.request_summary,
    f.status,
    f.assigned_to,
    f.response_date
FROM foi_requests f
JOIN properties p
    ON f.property_id = p.property_id
JOIN tenants t
    ON f.tenant_id = t.tenant_id;