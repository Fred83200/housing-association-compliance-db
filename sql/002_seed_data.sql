INSERT INTO properties (
    uprn, address_line_1, address_line_2, city, postcode, property_type, bedrooms, build_year, compliance_status, last_inspection_date
) VALUES
('UPRN0001', '12 Rosewood Court', NULL, 'Birmingham', 'B12 4TP', 'Flat', 2, 2004, 'Compliant', '2026-03-10'),
('UPRN0002', '88 Meadow Lane', 'Flat 3', 'Leeds', 'LS11 8AB', 'Flat', 1, 1998, 'Inspection Due', '2025-11-22'),
('UPRN0003', '4 Willow Park', NULL, 'Manchester', 'M14 6GH', 'House', 3, 1987, 'Compliant', '2026-01-17'),
('UPRN0004', '21 Oak View', NULL, 'Sheffield', 'S2 5PL', 'House', 4, 1975, 'Non-Compliant', '2025-09-14'),
('UPRN0005', '7 Kingsway House', 'Flat 8', 'Liverpool', 'L8 2TR', 'Flat', 2, 2010, 'Compliant', '2026-02-05');

INSERT INTO tenants (
    property_id, first_name, last_name, date_of_birth, email, phone, tenancy_start_date, tenancy_end_date, is_primary_tenant
) VALUES
(1, 'Sarah', 'Smith', '1988-04-12', 'sarah.smith@example.com', '07111111111', '2021-06-01', NULL, TRUE),
(2, 'Daniel', 'Evans', '1992-09-03', 'daniel.evans@example.com', '07222222222', '2023-01-15', NULL, TRUE),
(3, 'Amira', 'Rahman', '1985-11-20', 'amira.rahman@example.com', '07333333333', '2020-10-01', NULL, TRUE),
(4, 'John', 'Baker', '1979-01-08', 'john.baker@example.com', '07444444444', '2019-03-10', NULL, TRUE),
(5, 'Leah', 'Turner', '1990-07-29', 'leah.turner@example.com', '07555555555', '2022-08-22', NULL, TRUE);

INSERT INTO contractors (
    contractor_name, specialism, email, phone, active
) VALUES
('SafeHeat Services Ltd', 'Boiler Repair', 'contact@safeheat.example.com', '02070000001', TRUE),
('DryHome Solutions', 'Damp and Mould', 'hello@dryhome.example.com', '02070000002', TRUE),
('BrightSpark Electrical', 'Electrical Inspection', 'ops@brightspark.example.com', '02070000003', TRUE),
('Shield Fire Doors', 'Fire Safety', 'info@shieldfire.example.com', '02070000004', TRUE),
('RoofFix UK', 'Roofing', 'support@rooffix.example.com', '02070000005', TRUE);

INSERT INTO repair_records (
    property_id, contractor_id, reported_date, scheduled_date, completed_date, repair_category, description, status, cost, notes
) VALUES
(1, 1, '2026-01-05', '2026-01-07', '2026-01-07', 'Boiler Repair', 'Tenant reported no heating or hot water.', 'Completed', 245.00, 'Boiler pressure restored and valve replaced.'),
(1, 2, '2026-02-11', '2026-02-14', '2026-02-16', 'Damp and Mould', 'Mould growth reported in bedroom corner.', 'Completed', 410.50, 'Wall treated and ventilation advice provided.'),
(2, 3, '2026-03-03', '2026-03-06', NULL, 'Electrical Inspection', 'Sockets in kitchen tripping fuse board.', 'In Progress', 180.00, 'Follow-up visit required.'),
(4, 4, '2025-12-19', '2025-12-22', '2025-12-22', 'Fire Door Replacement', 'Front entrance fire door not closing correctly.', 'Completed', 620.00, 'Door replaced and certified.'),
(3, 5, '2026-02-02', '2026-02-05', '2026-02-08', 'Roof Leak', 'Water ingress reported in loft after rain.', 'Completed', 980.00, 'Broken tiles replaced and flashing sealed.');

INSERT INTO foi_requests (
    tenant_id, property_id, request_reference, request_date, due_date, request_type, request_summary, status, assigned_to, response_date
) VALUES
(1, 1, 'FOI-2026-0001', '2026-03-01', '2026-03-31', 'Repairs History', 'Request for all repair records and contractor visits for the past 24 months.', 'Responded', 'Caseworker A', '2026-03-20'),
(2, 2, 'FOI-2026-0002', '2026-03-10', '2026-04-09', 'Electrical Safety', 'Request for all electrical inspection records and maintenance actions.', 'Open', 'Caseworker B', NULL),
(3, 3, 'FOI-2026-0003', '2026-02-15', '2026-03-17', 'Roof and Structural Repairs', 'Request for roof repair reports, contractor notes and inspection records.', 'Closed', 'Caseworker C', '2026-03-05'),
(4, 4, 'FOI-2026-0004', '2026-03-18', '2026-04-17', 'Fire Safety', 'Request for fire door inspection and replacement records.', 'In Review', 'Caseworker D', NULL),
(5, 5, 'FOI-2026-0005', '2026-04-01', '2026-05-01', 'Tenancy and Repairs', 'Request for tenancy correspondence and repairs raised since move-in date.', 'Open', 'Caseworker A', NULL);