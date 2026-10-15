import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database import get_db_connection, init_db

def seed_database():
    """
    Initializes and populates the database with realistic sample demonstration
    records for college project evaluation and presentation.
    """
    init_db()
    conn = get_db_connection()
    c = conn.cursor()

    # Clear existing data for fresh demo seed
    c.execute("DELETE FROM redistribution_requests")
    c.execute("DELETE FROM donations")
    c.execute("DELETE FROM predictions_log")
    c.execute("DELETE FROM users")

    # Sample Demonstration Users
    # Password for admin is 'admin123', donors: 'donor123', recipients: 'recipient123'
    users_data = [
        # Admin
        ('admin', 'admin@ecodine.edu', generate_password_hash('admin123'), 'admin',
         'Campus Sustainability Cell & Digital Thinking Lab', 'Dr. Ramesh Sharma', '+91 98230 11223',
         'Academic Block 4, Campus Hub', 'Metro City', 500, 1),
         
        # Donors (Canteens, Messes, Restaurants)
        ('apex_canteen', 'canteen@apexuniv.edu', generate_password_hash('donor123'), 'donor',
         'Apex University Central Canteen', 'Chef Sundar Rajan', '+91 98450 12345',
         'Central Food Court, Campus East', 'Metro City', 350, 1),
         
        ('hostel_mess', 'mess3@apexuniv.edu', generate_password_hash('donor123'), 'donor',
         'Boys Hostel Dining Facility #3', 'Manager K. Verma', '+91 98765 43210',
         'Hostel Zone Block C', 'Metro City', 450, 1),
         
        ('green_bites', 'manager@greenbites.com', generate_password_hash('donor123'), 'donor',
         'GreenBites Farm-To-Table Restaurant', 'Pooja Deshmukh', '+91 99234 56789',
         '14 Ring Road, Tech Park Avenue', 'Metro City', 200, 1),
         
        ('royal_bakers', 'contact@royalcrust.com', generate_password_hash('donor123'), 'donor',
         'Royal Crust Artisan Bakery & Cafe', 'Anand Kulkarni', '+91 97654 32198',
         'Shop 8, College Market Square', 'Metro City', 150, 1),

        # Recipients (NGOs, Shelters, Community Kitchens)
        ('annapoorna_ngo', 'relief@annapoorna.org', generate_password_hash('recipient123'), 'recipient',
         'Annapoorna Hunger Relief Foundation', 'Sunita Rao (Director)', '+91 94220 77889',
         'Plot 45, Gandhi Nagar Community Center', 'Metro City', 300, 1),
         
        ('hope_shelter', 'contact@hopehaven.org', generate_password_hash('recipient123'), 'recipient',
         'Hope Haven Night Shelter & Community Kitchen', 'Father Joseph Thomas', '+91 93710 44556',
         'Old Railway Station Road', 'Metro City', 150, 1),
         
        ('bal_vikas', 'trustee@balvikashome.org', generate_password_hash('recipient123'), 'recipient',
         'Bal Vikas Children Welfare Home', 'Mrs. Meenakshi Joshi', '+91 98221 66778',
         'Sector 12, Prerana Enclave', 'Metro City', 85, 1),
         
        ('sandhya_care', 'info@sandhyadeep.org', generate_password_hash('recipient123'), 'recipient',
         'Sandhya Deep Senior Citizen Home', 'Col. R.K. Nair (Retd.)', '+91 98500 33445',
         'Green Valley Road, Near Lake View', 'Metro City', 60, 1)
    ]

    c.executemany('''
        INSERT INTO users (username, email, password_hash, role, org_name, contact_person, phone, address, city, capacity_servings, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users_data)

    # Fetch inserted user IDs
    c.execute("SELECT id, username FROM users")
    user_map = {row['username']: row['id'] for row in c.fetchall()}

    now = datetime.now()
    
    # Sample Donations across different urgency, food types and statuses
    donations_data = [
        # Available - Urgent (Expiring in 3.5 hours)
        (user_map['apex_canteen'], 'Chef Sundar Rajan', 'Apex University Central Canteen',
         'Vegetable Biryani & Mirchi Salan', 'Cooked Meals', 28.5, 70,
         (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
         (now + timedelta(hours=3, minutes=30)).strftime('%Y-%m-%d %H:%M'),
         'Central Food Court Kitchen Dock 2, Campus East', 'Metro City',
         '+91 98450 12345', 'canteen@apexuniv.edu', 'Vegetarian', 'Hot Holding',
         'Prepared for lunch session. Freshly packed into stainless insulated food warmers. Hot and safe.',
         'Available'),

        # Available - Medium Urgency (Expiring in 6 hours)
        (user_map['hostel_mess'], 'Manager K. Verma', 'Boys Hostel Dining Facility #3',
         'Jeera Rice, Yellow Dal Tadka & Chapati', 'Cooked Meals', 38.0, 95,
         (now - timedelta(hours=1, minutes=30)).strftime('%Y-%m-%d %H:%M'),
         (now + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M'),
         'Hostel Zone Mess Gate B', 'Metro City',
         '+91 98765 43210', 'mess3@apexuniv.edu', 'Vegetarian', 'Refrigerated (Cold Chain)',
         'Chilled immediately after afternoon lunch shift. Needs reheating before consumption.',
         'Available'),

        # Available - Bakery (Expiring in 18 hours)
        (user_map['royal_bakers'], 'Anand Kulkarni', 'Royal Crust Artisan Bakery & Cafe',
         'Fresh Multigrain Bread, Croissants & Buns', 'Bakery & Bread', 16.0, 55,
         (now - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
         (now + timedelta(hours=18)).strftime('%Y-%m-%d %H:%M'),
         'Shop 8, College Market Square', 'Metro City',
         '+91 97654 32198', 'contact@royalcrust.com', 'Vegetarian', 'Room Temperature',
         'End-of-day fresh artisanal loaves and sandwich breads. Sealed in paper packs.',
         'Available'),

        # Available - Fresh Produce (Expiring in 36 hours)
        (user_map['green_bites'], 'Pooja Deshmukh', 'GreenBites Farm-To-Table Restaurant',
         'Assorted Fresh Apples, Bananas & Seasonal Melons', 'Fresh Produce', 22.0, 50,
         (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M'),
         (now + timedelta(hours=36)).strftime('%Y-%m-%d %H:%M'),
         '14 Ring Road, Tech Park Avenue Service Lane', 'Metro City',
         '+91 99234 56789', 'manager@greenbites.com', 'Vegan', 'Room Temperature',
         'High-grade whole surplus fruits, undamaged and washed. Ideal for daycare or shelter breakfast.',
         'Available'),

        # Requested (Pending pickup confirmation)
        (user_map['apex_canteen'], 'Chef Sundar Rajan', 'Apex University Central Canteen',
         'Paneer Butter Masala & Steamed Basmati Rice', 'Cooked Meals', 25.0, 60,
         (now - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'),
         (now + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
         'Central Food Court Kitchen Dock 2', 'Metro City',
         '+91 98450 12345', 'canteen@apexuniv.edu', 'Vegetarian', 'Refrigerated (Cold Chain)',
         'High protein vegetarian meal. Packed in food-grade plastic containers.',
         'Requested'),

        # Claimed (NGO vehicle en route)
        (user_map['green_bites'], 'Pooja Deshmukh', 'GreenBites Farm-To-Table Restaurant',
         'South Indian Tiffin Combo (Idli, Medu Vada, Sambar)', 'Cooked Meals', 19.0, 48,
         (now - timedelta(hours=3, minutes=30)).strftime('%Y-%m-%d %H:%M'),
         (now + timedelta(hours=4, minutes=30)).strftime('%Y-%m-%d %H:%M'),
         '14 Ring Road Tech Park', 'Metro City',
         '+91 99234 56789', 'manager@greenbites.com', 'Vegetarian', 'Hot Holding',
         'Claimed by Bal Vikas Home. Pickup vehicle dispatched.',
         'Claimed'),

        # Redistributed (Successfully rescued past 2 days)
        (user_map['hostel_mess'], 'Manager K. Verma', 'Boys Hostel Dining Facility #3',
         'Rajma Masala, Steamed Rice & Phulka Roti', 'Cooked Meals', 45.0, 115,
         (now - timedelta(days=1, hours=4)).strftime('%Y-%m-%d %H:%M'),
         (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
         'Hostel Zone Mess Gate B', 'Metro City',
         '+91 98765 43210', 'mess3@apexuniv.edu', 'Vegetarian', 'Room Temperature',
         'Successfully distributed to Hope Haven Night Shelter residents.',
         'Redistributed'),

        (user_map['royal_bakers'], 'Anand Kulkarni', 'Royal Crust Artisan Bakery & Cafe',
         'Pound Cakes, Fruit Breads & Sweet Buns', 'Dairy & Sweets', 14.5, 40,
         (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
         (now - timedelta(days=1, hours=12)).strftime('%Y-%m-%d %H:%M'),
         'Shop 8, College Market Square', 'Metro City',
         '+91 97654 32198', 'contact@royalcrust.com', 'Vegetarian', 'Room Temperature',
         'Rescued and delivered to Sandhya Deep Senior Home.',
         'Redistributed')
    ]

    c.executemany('''
        INSERT INTO donations (
            donor_id, donor_name, org_name, food_title, food_type, quantity_kg, estimated_meals,
            prep_datetime, expiry_datetime, pickup_address, city, contact_phone, contact_email,
            dietary_type, storage_requirement, notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', donations_data)

    # Fetch donation IDs
    c.execute("SELECT id, food_title, status FROM donations")
    donations_map = {row['food_title']: row['id'] for row in c.fetchall()}

    # Sample Redistribution Requests
    requests_data = [
        # Request on 'Paneer Butter Masala & Steamed Basmati Rice' (Status: Requested)
        (donations_map['Paneer Butter Masala & Steamed Basmati Rice'],
         user_map['annapoorna_ngo'], 'Annapoorna Hunger Relief Foundation',
         'Sunita Rao', '+91 94220 77889', 'Van / Mini-Truck', 60,
         (now + timedelta(hours=1, minutes=15)).strftime('%Y-%m-%d %H:%M'),
         'Our temperature-controlled food rescue van is in Sector 4 and can arrive within 45 mins.',
         92.5, 'Pending'),

        # Claim on 'South Indian Tiffin Combo (Idli, Medu Vada, Sambar)' (Status: Claimed)
        (donations_map['South Indian Tiffin Combo (Idli, Medu Vada, Sambar)'],
         user_map['bal_vikas'], 'Bal Vikas Children Welfare Home',
         'Mrs. Meenakshi Joshi', '+91 98221 66778', 'Car / Auto', 48,
         (now + timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M'),
         'Volunteer driver is picking this up for the evening children dinner routine.',
         88.0, 'Approved'),

        # Completed redistribution for historical tracking
        (donations_map['Rajma Masala, Steamed Rice & Phulka Roti'],
         user_map['hope_shelter'], 'Hope Haven Night Shelter & Community Kitchen',
         'Father Joseph Thomas', '+91 93710 44556', 'Van / Mini-Truck', 115,
         (now - timedelta(days=1, hours=2)).strftime('%Y-%m-%d %H:%M'),
         'Fully received in good condition and served to 115 shelter guests.',
         96.0, 'Completed')
    ]

    c.executemany('''
        INSERT INTO redistribution_requests (
            donation_id, recipient_id, recipient_org, contact_name, contact_phone,
            pickup_vehicle_type, beneficiary_count, estimated_pickup_time, request_notes,
            match_score, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', requests_data)

    # Sample Prediction Logs for historical insight
    pred_data = [
        (user_map['apex_canteen'], 'Cooked Meals', 85.0, 200, 190, 135,
         'College Canteen', 'Friday', 'Rainy/Storm', 28.5, 67, 'High',
         'Substantial surplus (25-40%). Trigger instant Smart Redistribution to nearby partner NGOs.'),
         
        (user_map['hostel_mess'], 'Cooked Meals', 110.0, 260, 250, 180,
         'Hostel Mess', 'Saturday', 'Sunny/Mild', 34.0, 80, 'High',
         'Substantial surplus (25-40%). Trigger instant Smart Redistribution to nearby partner NGOs.'),
         
        (user_map['royal_bakers'], 'Bakery & Bread', 35.0, 120, 120, 105,
         'Restaurant Daily', 'Wednesday', 'Sunny/Mild', 4.5, 15, 'Low',
         'Normal operational surplus (<10%). Can be safely chilled for tomorrow or staff distribution.')
    ]

    c.executemany('''
        INSERT INTO predictions_log (
            user_id, food_type, quantity_prepared_kg, meals_prepared, expected_attendance,
            meals_consumed, event_type, day_of_week, weather_condition, predicted_surplus_kg,
            predicted_surplus_meals, waste_risk_level, recommended_action
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', pred_data)

    conn.commit()
    conn.close()
    print("Database seeded with rich demonstration data successfully!")

if __name__ == '__main__':
    seed_database()
