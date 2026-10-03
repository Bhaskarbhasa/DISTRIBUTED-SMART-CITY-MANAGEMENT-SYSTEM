-- Create Enums
CREATE TYPE role_enum AS ENUM ('ADMIN', 'OPERATOR', 'ANALYST', 'VIEWER');

-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role role_enum NOT NULL DEFAULT 'VIEWER',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    details JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    result VARCHAR(50) NOT NULL
);

CREATE TABLE token_blacklist (
    id SERIAL PRIMARY KEY,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    blacklisted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    polygon_coordinates JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES zones(id),
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    firmware_version VARCHAR(50),
    last_ping TIMESTAMP WITH TIME ZONE,
    coordinates JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE traffic_configurations (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES zones(id),
    config_data JSONB NOT NULL,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emergency_records (
    id SERIAL PRIMARY KEY,
    incident_type VARCHAR(100) NOT NULL,
    description TEXT,
    zone_id INTEGER REFERENCES zones(id),
    status VARCHAR(50) NOT NULL,
    reported_by INTEGER REFERENCES users(id),
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert Users
-- Passwords are 'Admin@123', 'Operator@123', 'Analyst@123', 'Viewer@123'
INSERT INTO users (email, password_hash, role) VALUES 
('admin@smartcity.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ADMIN'),
('operator@smartcity.local', '$2b$12$w0.K/R8V5ZzYtL.B42Z3Luw8.T9lC1j5T4JtO5M2Wk3rR4x/H6iFq', 'OPERATOR'),
('analyst@smartcity.local', '$2b$12$K12Z1Q7b1x1M2W3E4R5T6O7P8A9S0D1F2G3H4J5K6L7Z8X9C0V', 'ANALYST'),
('viewer@smartcity.local', '$2b$12$M1N2B3V4C5X6Z7A8S9D0F1G2H3J4K5L6P7O8I9U0Y1T2R3E4W5Q', 'VIEWER');

-- Insert Zones
INSERT INTO zones (name, description, polygon_coordinates) VALUES
('ZONE-A', 'Downtown Commercial District', '[[0,0], [0,1], [1,1], [1,0]]'),
('ZONE-B', 'Residential North', '[[1,1], [1,2], [2,2], [2,1]]'),
('ZONE-C', 'Industrial Park South', '[[0,-1], [0,0], [1,0], [1,-1]]'),
('ZONE-D', 'University Campus', '[[-1,0], [-1,1], [0,1], [0,0]]'),
('ZONE-E', 'East Side Suburbs', '[[2,0], [2,1], [3,1], [3,0]]');
