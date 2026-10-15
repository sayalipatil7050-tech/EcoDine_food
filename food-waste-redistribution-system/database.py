import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'food_waste.db')

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('donor', 'recipient', 'admin')),
            org_name TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            capacity_servings INTEGER DEFAULT 100,
            is_verified INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Donations / Food Listings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER,
            donor_name TEXT NOT NULL,
            org_name TEXT NOT NULL,
            food_title TEXT NOT NULL,
            food_type TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            estimated_meals INTEGER NOT NULL,
            prep_datetime TEXT NOT NULL,
            expiry_datetime TEXT NOT NULL,
            pickup_address TEXT NOT NULL,
            city TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            contact_email TEXT,
            dietary_type TEXT NOT NULL,
            storage_requirement TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'Available' CHECK(status IN ('Available', 'Requested', 'Claimed', 'Redistributed', 'Cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')

    # Redistribution Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS redistribution_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donation_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            recipient_org TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            pickup_vehicle_type TEXT NOT NULL,
            beneficiary_count INTEGER NOT NULL,
            estimated_pickup_time TEXT NOT NULL,
            request_notes TEXT,
            match_score REAL DEFAULT 0,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Completed', 'Rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Predictions Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            food_type TEXT NOT NULL,
            quantity_prepared_kg REAL NOT NULL,
            meals_prepared INTEGER NOT NULL,
            expected_attendance INTEGER NOT NULL,
            meals_consumed INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            weather_condition TEXT NOT NULL,
            predicted_surplus_kg REAL NOT NULL,
            predicted_surplus_meals INTEGER NOT NULL,
            waste_risk_level TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()

def get_dashboard_metrics():
    """Calculates overall project metrics for the Dashboard."""
    conn = get_db_connection()
    c = conn.cursor()

    # Total listings
    c.execute("SELECT COUNT(*) FROM donations")
    total_listings = c.fetchone()[0]

    # Available surplus food
    c.execute("SELECT COALESCE(SUM(quantity_kg), 0), COALESCE(SUM(estimated_meals), 0) FROM donations WHERE status = 'Available'")
    avail_kg, avail_meals = c.fetchone()

    # Food successfully redistributed
    c.execute("SELECT COALESCE(SUM(quantity_kg), 0), COALESCE(SUM(estimated_meals), 0) FROM donations WHERE status = 'Redistributed'")
    redis_kg, redis_meals = c.fetchone()

    # Food in-transit / claimed
    c.execute("SELECT COALESCE(SUM(quantity_kg), 0), COALESCE(SUM(estimated_meals), 0) FROM donations WHERE status IN ('Requested', 'Claimed')")
    claimed_kg, claimed_meals = c.fetchone()

    # Estimated food waste reduced (all redistributed + claimed that avoids landfill)
    waste_reduced_kg = round(redis_kg + (claimed_kg * 0.9), 1)

    # CO2 reduction estimate: approx 2.5 kg CO2e per kg food rescued (FAO standard benchmark)
    co2_saved_kg = round(waste_reduced_kg * 2.5, 1)

    # Participant counts
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'donor'")
    donors_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role = 'recipient'")
    recipients_count = c.fetchone()[0]

    # Breakdown by food type
    c.execute("""
        SELECT food_type, 
               COUNT(*) as count, 
               COALESCE(SUM(quantity_kg), 0) as total_kg
        FROM donations
        GROUP BY food_type
        ORDER BY total_kg DESC
    """)
    type_breakdown = [dict(row) for row in c.fetchall()]

    # Breakdown by status
    c.execute("""
        SELECT status, COUNT(*) as count, COALESCE(SUM(quantity_kg), 0) as total_kg
        FROM donations
        GROUP BY status
    """)
    status_breakdown = {row['status']: {'count': row['count'], 'kg': round(row['total_kg'], 1)} for row in c.fetchall()}

    # Recent activity
    c.execute("""
        SELECT d.id, d.food_title, d.food_type, d.quantity_kg, d.estimated_meals, d.city, d.status, d.created_at, d.org_name
        FROM donations d
        ORDER BY d.created_at DESC
        LIMIT 6
    """)
    recent_donations = [dict(row) for row in c.fetchall()]

    # Total prediction runs
    c.execute("SELECT COUNT(*) FROM predictions_log")
    prediction_runs = c.fetchone()[0]

    conn.close()

    return {
        'total_listings': total_listings,
        'available_kg': round(avail_kg, 1),
        'available_meals': int(avail_meals),
        'redistributed_kg': round(redis_kg, 1),
        'redistributed_meals': int(redis_meals),
        'waste_reduced_kg': waste_reduced_kg,
        'co2_saved_kg': co2_saved_kg,
        'donors_count': donors_count,
        'recipients_count': recipients_count,
        'type_breakdown': type_breakdown,
        'status_breakdown': status_breakdown,
        'recent_donations': recent_donations,
        'prediction_runs': prediction_runs
    }

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
