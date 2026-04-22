-- 1. Find all tenants and their properties
SELECT
    t.tenant_id,
    t.first_name,
    t.last_name,
    p.address_line_1,
    p.city,
    p.postcode
FROM tenants t
JOIN properties p
    ON t.property_id = p.property_id
ORDER BY t.tenant_id;

-- 2. Find all repair records for a given postcode
SELECT
    p.address_line_1,
    p.postcode,
    r.repair_category,
    r.description,
    r.status,
    r.reported_date,
    r.completed_date
FROM properties p
JOIN repair_records r
    ON p.property_id = r.property_id
WHERE p.postcode = 'B12 4TP';

-- 3. Find all repairs completed by each contractor
SELECT
    c.contractor_name,
    r.repair_category,
    r.description,
    r.completed_date
FROM contractors c
JOIN repair_records r
    ON c.contractor_id = r.contractor_id
ORDER BY c.contractor_name;

-- 4. Find FOI requests and their status
SELECT
    f.request_reference,
    f.request_type,
    f.status,
    f.request_date,
    f.due_date,
    t.first_name,
    t.last_name
FROM foi_requests f
JOIN tenants t
    ON f.tenant_id = t.tenant_id
ORDER BY f.request_date DESC;

-- 5. Find overdue FOI requests
SELECT
    request_reference,
    request_type,
    status,
    due_date,
    assigned_to
FROM foi_requests
WHERE due_date < CURRENT_DATE
  AND response_date IS NULL;

-- 6. Find all records linked to a specific tenant
SELECT
    t.first_name,
    t.last_name,
    p.address_line_1,
    f.request_reference,
    f.request_summary
FROM tenants t
JOIN properties p
    ON t.property_id = p.property_id
LEFT JOIN foi_requests f
    ON t.tenant_id = f.tenant_id
WHERE t.last_name = 'Smith';

-- 7. Find property repairs with contractor details
SELECT
    p.address_line_1,
    p.postcode,
    r.repair_category,
    r.status,
    c.contractor_name,
    c.specialism
FROM repair_records r
JOIN properties p
    ON r.property_id = p.property_id
LEFT JOIN contractors c
    ON r.contractor_id = c.contractor_id
ORDER BY p.address_line_1;