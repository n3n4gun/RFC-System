-- Executed by the official PostgreSQL image in POSTGRES_DB on first startup.
BEGIN;

-- Keep IDs as strings: the application uses uuid.uuid4().hex and expects str.
CREATE TABLE users_table (
    user_id VARCHAR(32) PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL CHECK (char_length(full_name) >= 5),
    email VARCHAR(254) NOT NULL UNIQUE,
    department VARCHAR(25) NOT NULL CHECK (char_length(department) >= 3),
    password TEXT NOT NULL,
    registration_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE active_users (
    user_id VARCHAR(32) PRIMARY KEY REFERENCES users_table (user_id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE applications_table (
    application_id VARCHAR(32) PRIMARY KEY,
    title VARCHAR(120) NOT NULL CHECK (char_length(title) >= 5),
    service VARCHAR(60) NOT NULL CHECK (char_length(service) >= 1),
    priority VARCHAR(8) NOT NULL
        CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    description VARCHAR(2000) NOT NULL CHECK (char_length(description) >= 20),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

COMMIT;
