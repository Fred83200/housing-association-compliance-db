CREATE USER foundry_reader WITH PASSWORD 'replace-with-secure-password';

GRANT CONNECT ON DATABASE housing_compliance_demo TO foundry_reader;
GRANT USAGE ON SCHEMA public TO foundry_reader;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO foundry_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO foundry_reader;