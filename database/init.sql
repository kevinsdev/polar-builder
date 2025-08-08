-- PostgreSQL Database Initialization for Polar Builder
-- This script creates the necessary tables for the Polar Builder application

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create boats table
CREATE TABLE IF NOT EXISTS boats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    boat_type VARCHAR(50) NOT NULL,
    class_design VARCHAR(100),
    year_built INTEGER,
    loa DECIMAL(5,2),
    lwl DECIMAL(5,2),
    beam DECIMAL(5,2),
    draft DECIMAL(5,2),
    displacement INTEGER,
    sail_area DECIMAL(6,2),
    keel_type VARCHAR(50),
    rig_type VARCHAR(50),
    hull_material VARCHAR(50),
    crew_size INTEGER,
    rating_system VARCHAR(50),
    rating_value VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create log_files table
CREATE TABLE IF NOT EXISTS log_files (
    id SERIAL PRIMARY KEY,
    boat_id INTEGER NOT NULL REFERENCES boats(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    s3_key VARCHAR(500) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT
);

-- Create polars table
CREATE TABLE IF NOT EXISTS polars (
    id SERIAL PRIMARY KEY,
    boat_id INTEGER NOT NULL REFERENCES boats(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    wind_speeds TEXT, -- JSON array of wind speeds
    wind_angles TEXT, -- JSON array of wind angles
    boat_speeds TEXT, -- JSON 2D array of boat speeds
    s3_key VARCHAR(500),
    created_from_logs TEXT, -- JSON array of log file IDs used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_boats_user_id ON boats(user_id);
CREATE INDEX IF NOT EXISTS idx_log_files_boat_id ON log_files(boat_id);
CREATE INDEX IF NOT EXISTS idx_polars_boat_id ON polars(boat_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_boats_updated_at BEFORE UPDATE ON boats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_polars_updated_at BEFORE UPDATE ON polars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert a default admin user (password: admin123)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, full_name) 
VALUES ('admin', 'admin@polarbuilder.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtO5S8VyoS', 'Administrator')
ON CONFLICT (username) DO NOTHING;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO polar_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO polar_user;

