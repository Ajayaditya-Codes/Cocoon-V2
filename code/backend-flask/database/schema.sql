-- Drop existing tables if they exist to avoid conflicts
DROP TABLE IF EXISTS service_requests;
DROP TABLE IF EXISTS professionals;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS credentials;

-- Create Credentials Table
CREATE TABLE credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    userType TEXT CHECK(userType IN ('customer', 'professional', 'admin')) DEFAULT 'customer' NOT NULL,
    email TEXT NOT NULL,
    blocked INTEGER
        CHECK(blocked IN (0, 1))
        NOT NULL DEFAULT 0,
    UNIQUE (username, email)
);

-- Create Services Table
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT
);

-- Create Customers Table
CREATE TABLE customers (
    credential_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    address TEXT,
    pincode TEXT NOT NULL,
    date_of_joining DATE DEFAULT (CURRENT_DATE),
    phone INTEGER NOT NULL,
    FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE CASCADE
);

-- Create Service Professionals Table
CREATE TABLE professionals (
    credential_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    service_provided TEXT NOT NULL,
    pincode TEXT NOT NULL,
    experience INTEGER NOT NULL,
    phone INTEGER NOT NULL,
    verified INTEGER
        CHECK(verified IN (0, 1))
        NOT NULL DEFAULT 0,
    documents TEXT NOT NULL,
    date_of_joining DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE CASCADE
);

-- Create Service Requests Table
CREATE TABLE service_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,    
    customer_id INTEGER NOT NULL,
    professional_id INTEGER,
    date_of_request TEXT NOT NULL DEFAULT (CURRENT_DATE),
    date_of_service DATE NOT NULL,
    service_description TEXT,
    price REAL NOT NULL,
    service_status TEXT 
        CHECK(service_status IN ('requested', 'quoted', 'assigned', 'closed')) 
        NOT NULL DEFAULT 'requested',
    rating INTEGER NOT NULL DEFAULT 0,
    review TEXT,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(credential_id) ON DELETE CASCADE,
    FOREIGN KEY (professional_id) REFERENCES professionals(credential_id) ON DELETE CASCADE
);

-- Insert initial admin credentials with hashed password
INSERT INTO credentials (username, password, email, userType) 
VALUES ('admin', 'pbkdf2:sha256:260000$S0VliMoOhFRbmx3Z$c933dff22295e34fb1a3d0d0be937a510e8708aa30decebc18a3188291aaa010', 'admin@cocoon.com', 'admin');

-- Insert initial services
INSERT INTO services (name, price, description) VALUES
    ('Plumbing', 500, 'All types of plumbing repairs and installations'),
    ('Electrical', 750, 'Electrical repairs, wiring, and installations'),
    ('Cleaning', 300, 'Home and office cleaning services'),
    ('Gardening', 400, 'Lawn care, landscaping, and gardening services'),
    ('Carpentry', 600, 'Woodworking, repairs, and furniture assembly');
