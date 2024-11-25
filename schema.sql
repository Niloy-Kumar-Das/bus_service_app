-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'passenger')) DEFAULT 'passenger',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Routes Table
CREATE TABLE IF NOT EXISTS routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_name TEXT NOT NULL,
    stops TEXT NOT NULL -- Optionally normalize into a separate table if needed
);

-- Create Drivers Table
CREATE TABLE IF NOT EXISTS drivers (
    driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    license_number TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    address TEXT
);

-- Create Buses Table
CREATE TABLE IF NOT EXISTS buses (
    bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number TEXT NOT NULL UNIQUE,
    route_id INTEGER NOT NULL,
    ticket_price REAL NOT NULL,
    is_prebooked INTEGER DEFAULT 0,
    prebooked_by INTEGER,
    capacity INTEGER NOT NULL,
    driver_id1 INTEGER,
    driver_id2 INTEGER,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id1) REFERENCES drivers(driver_id) ON DELETE SET NULL,
    FOREIGN KEY (driver_id2) REFERENCES drivers(driver_id) ON DELETE SET NULL,
    FOREIGN KEY (prebooked_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Create Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_id INTEGER NOT NULL,
    seat_number INTEGER NOT NULL,
    seat_id TEXT NOT NULL UNIQUE,
    status TEXT CHECK(status IN ('sold', 'unsold')) DEFAULT 'unsold',
    price REAL NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Create Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bus_id INTEGER NOT NULL,
    comment TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE
);

-- Create Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bus_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE
);

-- Create Prebooked Buses Table
CREATE TABLE IF NOT EXISTS prebooked_buses (
    prebook_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bus_id INTEGER NOT NULL,
    prebook_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE
);

-- Create Schedules Table
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    departure_date TEXT NOT NULL, -- In ISO 8601 (YYYY-MM-DD) format
    departure_time TEXT NOT NULL, -- In 24-hour format (HH:MM)
    arrival_time TEXT NOT NULL,   -- In 24-hour format (HH:MM)
    FOREIGN KEY (bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE,
    UNIQUE (bus_id, departure_date, departure_time) -- Prevent duplicate schedules
);

-- Create Driver Assignments Table (Optional if not using driver columns in buses)
CREATE TABLE IF NOT EXISTS driver_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
);

