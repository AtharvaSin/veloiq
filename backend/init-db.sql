-- Runs automatically on first container start via docker-entrypoint-initdb.d
-- Creates the test database alongside the main veloiq database (already created by POSTGRES_DB env var)

CREATE DATABASE veloiq_test;

-- Grant privileges to the veloiq user on both databases
GRANT ALL PRIVILEGES ON DATABASE veloiq TO veloiq;
GRANT ALL PRIVILEGES ON DATABASE veloiq_test TO veloiq;

-- Enable pgcrypto for gen_random_uuid() on both databases
\c veloiq
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\c veloiq_test
CREATE EXTENSION IF NOT EXISTS pgcrypto;
