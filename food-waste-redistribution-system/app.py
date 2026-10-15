import os
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db, get_dashboard_metrics
from ml_model import predict_surplus, get_or_load_model
from matching import calculate_match_score, calculate_urgency_score

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'eco_dine_college_project_secret_2026_key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)

# Ensure database and model are initialized on boot
with app.app_context():
    init_db()
    try:
        get_or_load_model()
    except Exception as e:
        print("Model pre-load notice:", e)

# -------------------------------------------------------------
# Authentication & Role Decorators
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in first.", "warning")
                return redirect(url_for('login'))
            if session.get('role') not in roles and session.get('role') != 'admin':
                flash("You do not have permission to access that resource.", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.context_processor
def inject_global_vars():
    """Injects current user and date context into all Jinja2 templates."""
    return {
        'current_user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'org_name': session.get('org_name'),
            'city': session.get('city')
        } if 'user_id' in session else None,
        'current_year': datetime.now().year
    }

# -------------------------------------------------------------
# 1. HOME PAGE
# -------------------------------------------------------------
@app.route('/')
def index():
    metrics = get_dashboard_metrics()
    return render_template('index.html', metrics=metrics)

# -------------------------------------------------------------
# 2. DASHBOARD
# -------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard.html', metrics=metrics)

# -------------------------------------------------------------
# 3. FOOD WASTE PREDICTION
# -------------------------------------------------------------
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction_result = None
    input_values = {
        'food_type': 'Cooked Meals',
        'event_type': 'College Canteen',
        'day_of_week': datetime.now().strftime('%A'),
        'weather_condition': 'Sunny/Mild',
        'quantity_prepared_kg': 60.0,
        'meals_prepared': 150,
        'expected_attendance': 140,
        'meals_consumed': 95,
        'historical_waste_rate': 0.12
    }

    if request.method == 'POST':
        try:
            food_type = request.form.get('food_type', 'Cooked Meals')
            event_type = request.form.get('event_type', 'College Canteen')
            day_of_week = request.form.get('day_of_week', 'Friday')
            weather_condition = request.form.get('weather_condition', 'Sunny/Mild')
            qty_prepared = float(request.form.get('quantity_prepared_kg', 0))
            meals_prepared = int(request.form.get('meals_prepared', 0))
            expected_att = int(request.form.get('expected_attendance', 0))
            meals_consumed = int(request.form.get('meals_consumed', 0))
            hist_waste = float(request.form.get('historical_waste_rate', 0.10))

            # Store submitted values for re-rendering form
            input_values = {
                'food_type': food_type,
                'event_type': event_type,
                'day_of_week': day_of_week,
                'weather_condition': weather_condition,
                'quantity_prepared_kg': qty_prepared,
                'meals_prepared': meals_prepared,
                'expected_attendance': expected_att,
                'meals_consumed': meals_consumed,
                'historical_waste_rate': hist_waste
            }

            # Validation
            if qty_prepared <= 0 or meals_prepared <= 0:
                flash("Prepared quantity and meal count must be greater than zero.", "danger")
            elif meals_consumed > meals_prepared:
                flash("Meals consumed cannot exceed total meals prepared.", "warning")
            else:
                # Run ML Prediction
                prediction_result = predict_surplus(
                    food_type=food_type,
                    event_type=event_type,
                    day_of_week=day_of_week,
                    weather_condition=weather_condition,
                    quantity_prepared_kg=qty_prepared,
                    meals_prepared=meals_prepared,
                    expected_attendance=expected_att,
                    meals_consumed=meals_consumed,
                    historical_waste_rate=hist_waste
                )

                # Save prediction to SQLite database log
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO predictions_log (
                        user_id, food_type, quantity_prepared_kg, meals_prepared,
                        expected_attendance, meals_consumed, event_type, day_of_week,
                        weather_condition, predicted_surplus_kg, predicted_surplus_meals,
                        waste_risk_level, recommended_action
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session.get('user_id'), food_type, qty_prepared, meals_prepared,
                    expected_att, meals_consumed, event_type, day_of_week,
                    weather_condition, prediction_result['predicted_surplus_kg'],
                    prediction_result['predicted_surplus_meals'],
                    prediction_result['risk_level'], prediction_result['recommended_action']
                ))
                conn.commit()
                conn.close()

                flash("Surplus food prediction calculated using the AI Random Forest model.", "success")
        except ValueError as ve:
            flash(f"Invalid numeric input: {ve}", "danger")
        except Exception as e:
            flash(f"Error computing prediction: {str(e)}", "danger")

    return render_template('predict.html', result=prediction_result, form=input_values)

# -------------------------------------------------------------
# 4. FOOD DONATION PAGE
# -------------------------------------------------------------
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    # Pre-population parameters (e.g. from /predict button)
    prefill = {
        'food_type': request.args.get('food_type', 'Cooked Meals'),
        'quantity_kg': request.args.get('quantity_kg', ''),
        'estimated_meals': request.args.get('meals', ''),
        'food_title': request.args.get('title', '')
    }

    if request.method == 'POST':
        donor_name = request.form.get('donor_name', '').strip()
        org_name = request.form.get('org_name', '').strip()
        food_title = request.form.get('food_title', '').strip()
        food_type = request.form.get('food_type', 'Cooked Meals')
        quantity_kg = request.form.get('quantity_kg', 0)
        estimated_meals = request.form.get('estimated_meals', 0)
        prep_datetime = request.form.get('prep_datetime', '').strip()
        expiry_datetime = request.form.get('expiry_datetime', '').strip()
        pickup_address = request.form.get('pickup_address', '').strip()
        city = request.form.get('city', 'Metro City').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        dietary_type = request.form.get('dietary_type', 'Vegetarian')
        storage_requirement = request.form.get('storage_requirement', 'Room Temperature')
        notes = request.form.get('notes', '').strip()

        # Validation
        if not (donor_name and org_name and food_title and pickup_address and contact_phone and prep_datetime and expiry_datetime):
            flash("Please complete all required fields.", "danger")
            return render_template('donate.html', form_data=request.form, prefill=prefill)

        try:
            qty_float = float(quantity_kg)
            meals_int = int(estimated_meals)
            if qty_float <= 0 or meals_int <= 0:
                flash("Quantity (kg) and estimated meals must be positive numbers.", "danger")
                return render_template('donate.html', form_data=request.form, prefill=prefill)
        except ValueError:
            flash("Quantity and meals must be valid numeric values.", "danger")
            return render_template('donate.html', form_data=request.form, prefill=prefill)

        # Insert into SQLite
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO donations (
                donor_id, donor_name, org_name, food_title, food_type, quantity_kg, estimated_meals,
                prep_datetime, expiry_datetime, pickup_address, city, contact_phone, contact_email,
                dietary_type, storage_requirement, notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available')
        ''', (
            session.get('user_id'), donor_name, org_name, food_title, food_type, qty_float, meals_int,
            prep_datetime, expiry_datetime, pickup_address, city, contact_phone, contact_email,
            dietary_type, storage_requirement, notes
        ))
        conn.commit()
        new_donation_id = c.lastrowid
        conn.close()

        flash(f"Surplus food listing '{food_title}' submitted successfully! It is now live in the Smart Redistribution network.", "success")
        return redirect(url_for('redistribution', highlight=new_donation_id))

    # Pre-populate with logged-in user details if available
    user_defaults = {}
    if 'user_id' in session:
        conn = get_db_connection()
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
        if user_row:
            user_defaults = {
                'donor_name': user_row['contact_person'],
                'org_name': user_row['org_name'],
                'pickup_address': user_row['address'],
                'city': user_row['city'],
                'contact_phone': user_row['phone'],
                'contact_email': user_row['email']
            }

    # Set default dates
    now = datetime.now()
    default_prep = now.strftime('%Y-%m-%dT%H:%M')
    default_expiry = (now + timedelta(hours=6)).strftime('%Y-%m-%dT%H:%M')

    return render_template('donate.html',
                           user_defaults=user_defaults,
                           prefill=prefill,
                           default_prep=default_prep,
                           default_expiry=default_expiry)

# -------------------------------------------------------------
# 5. SMART REDISTRIBUTION
# -------------------------------------------------------------
@app.route('/redistribution')
def redistribution():
    city_filter = request.args.get('city', '').strip()
    food_type_filter = request.args.get('food_type', '').strip()
    diet_filter = request.args.get('diet', '').strip()
    status_filter = request.args.get('status', 'Available').strip()
    search_query = request.args.get('q', '').strip()
    highlight_id = request.args.get('highlight', type=int)

    # Active recipient profile for match calculation
    # If user is logged in as recipient, use their profile. Otherwise, allow selecting demo recipient persona.
    demo_recipient_id = request.args.get('demo_recipient', type=int)
    
    conn = get_db_connection()
    c = conn.cursor()

    # Determine recipient context for smart matching
    recipient_profile = None
    if session.get('role') == 'recipient' and 'user_id' in session:
        recipient_profile = c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    elif demo_recipient_id:
        recipient_profile = c.execute("SELECT * FROM users WHERE id = ? AND role = 'recipient'", (demo_recipient_id,)).fetchone()
    else:
        # Default fallback recipient for demonstrative smart matching
        recipient_profile = c.execute("SELECT * FROM users WHERE role = 'recipient' LIMIT 1").fetchone()

    recipient_dict = dict(recipient_profile) if recipient_profile else {
        'city': 'Metro City',
        'capacity_servings': 200,
        'org_name': 'Sample Recipient NGO'
    }

    # Build query
    query = "SELECT * FROM donations WHERE 1=1"
    params = []

    if status_filter and status_filter != 'All':
        query += " AND status = ?"
        params.append(status_filter)
    if city_filter and city_filter != 'All':
        query += " AND city = ?"
        params.append(city_filter)
    if food_type_filter and food_type_filter != 'All':
        query += " AND food_type = ?"
        params.append(food_type_filter)
    if diet_filter and diet_filter != 'All':
        query += " AND dietary_type = ?"
        params.append(diet_filter)
    if search_query:
        query += " AND (food_title LIKE ? OR org_name LIKE ? OR pickup_address LIKE ?)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term])

    query += " ORDER BY CASE WHEN status = 'Available' THEN 1 ELSE 2 END, created_at DESC"
    
    c.execute(query, params)
    raw_donations = [dict(row) for row in c.fetchall()]

    # Apply Smart Matching algorithm to all listings
    listings = []
    for d in raw_donations:
        match_info = calculate_match_score(d, recipient_dict)
        d['smart_match'] = match_info
        listings.append(d)

    # If sorted by relevance/match score for 'Available'
    listings.sort(key=lambda x: (x['status'] != 'Available', -x['smart_match']['match_score']))

    # Fetch unique filter choices
    c.execute("SELECT DISTINCT city FROM donations WHERE city IS NOT NULL AND city != ''")
    available_cities = [r['city'] for r in c.fetchall()]

    c.execute("SELECT DISTINCT food_type FROM donations")
    available_food_types = [r['food_type'] for r in c.fetchall()]

    # Fetch all recipient organizations for demo persona switcher
    c.execute("SELECT id, org_name, city, capacity_servings FROM users WHERE role = 'recipient'")
    recipient_options = [dict(r) for r in c.fetchall()]

    conn.close()

    return render_template(
        'redistribution.html',
        listings=listings,
        cities=available_cities,
        food_types=available_food_types,
        recipient_profile=recipient_dict,
        recipient_options=recipient_options,
        current_filters={
            'city': city_filter,
            'food_type': food_type_filter,
            'diet': diet_filter,
            'status': status_filter,
            'q': search_query,
            'demo_recipient': demo_recipient_id
        },
        highlight_id=highlight_id
    )

# -------------------------------------------------------------
# 5b. CLAIM / REQUEST DONATION ACTION
# -------------------------------------------------------------
@app.route('/claim-food', methods=['POST'])
def claim_food():
    donation_id = request.form.get('donation_id', type=int)
    recipient_org = request.form.get('recipient_org', '').strip()
    contact_name = request.form.get('contact_name', '').strip()
    contact_phone = request.form.get('contact_phone', '').strip()
    pickup_vehicle = request.form.get('pickup_vehicle_type', 'Van / Mini-Truck')
    beneficiaries = request.form.get('beneficiary_count', 50, type=int)
    eta = request.form.get('estimated_pickup_time', '').strip()
    notes = request.form.get('request_notes', '').strip()

    if not (donation_id and recipient_org and contact_name and contact_phone and eta):
        flash("Please provide all required pickup claim details.", "danger")
        return redirect(url_for('redistribution'))

    conn = get_db_connection()
    c = conn.cursor()

    # Check donation status
    donation = c.execute("SELECT * FROM donations WHERE id = ?", (donation_id,)).fetchone()
    if not donation:
        conn.close()
        flash("Food donation not found.", "danger")
        return redirect(url_for('redistribution'))

    if donation['status'] not in ['Available', 'Requested']:
        conn.close()
        flash("This donation is no longer available for claiming.", "warning")
        return redirect(url_for('redistribution'))

    recipient_id = session.get('user_id')
    if not recipient_id:
        # Assign to first matching recipient user or admin
        rec_user = c.execute("SELECT id FROM users WHERE org_name = ? OR role = 'recipient' LIMIT 1", (recipient_org,)).fetchone()
        recipient_id = rec_user['id'] if rec_user else 1

    # Record the request
    c.execute('''
        INSERT INTO redistribution_requests (
            donation_id, recipient_id, recipient_org, contact_name, contact_phone,
            pickup_vehicle_type, beneficiary_count, estimated_pickup_time, request_notes,
            match_score, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved')
    ''', (
        donation_id, recipient_id, recipient_org, contact_name, contact_phone,
        pickup_vehicle, beneficiaries, eta, notes, 92.0
    ))

    # Update donation status to Claimed
    c.execute("UPDATE donations SET status = 'Claimed' WHERE id = ?", (donation_id,))
    conn.commit()
    conn.close()

    flash(f"Claim successfully placed for '{donation['food_title']}'! The donor has been notified with your pickup ETA ({eta}).", "success")
    return redirect(url_for('redistribution', status='All', highlight=donation_id))

# -------------------------------------------------------------
# 6. LOGIN, REGISTRATION & LOGOUT
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash("Please enter both username/email and password.", "danger")
            return render_template('login.html')

        conn = get_db_connection()
        c = conn.cursor()
        user = c.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['org_name'] = user['org_name']
            session['city'] = user['city']
            flash(f"Welcome back, {user['contact_person']} ({user['org_name']})!", "success")
            
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'donor':
                return redirect(url_for('donate'))
            else:
                return redirect(url_for('redistribution'))
        else:
            flash("Invalid credentials. Please verify your username and password.", "danger")

    return render_template('login.html')

@app.route('/quick-login/<role>')
def quick_login(role):
    """
    Convenient 1-click login helper for college evaluators and demonstration purposes.
    Allows testing Donor, Recipient, and Administrator roles instantly.
    """
    conn = get_db_connection()
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE role = ? LIMIT 1", (role,)).fetchone()
    conn.close()

    if user:
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['org_name'] = user['org_name']
        session['city'] = user['city']
        flash(f"Demonstration mode: Logged in as {role.upper()} ({user['org_name']}).", "info")
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'donor':
            return redirect(url_for('donate'))
        else:
            return redirect(url_for('redistribution'))
    
    flash(f"No demo user found for role '{role}'. Please seed the database first.", "warning")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'donor')
        org_name = request.form.get('org_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', 'Metro City').strip()
        capacity = request.form.get('capacity_servings', 100, type=int)

        # Basic validations
        if not (username and email and password and role and org_name and contact_person and phone and address):
            flash("Please fill in all mandatory fields.", "danger")
            return render_template('register.html', form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', form_data=request.form)

        conn = get_db_connection()
        c = conn.cursor()
        
        # Check uniqueness
        existing = c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
        if existing:
            conn.close()
            flash("Username or email already registered. Please login instead.", "warning")
            return render_template('register.html', form_data=request.form)

        # Insert new user
        password_hash = generate_password_hash(password)
        c.execute('''
            INSERT INTO users (username, email, password_hash, role, org_name, contact_person, phone, address, city, capacity_servings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, role, org_name, contact_person, phone, address, city, capacity))
        conn.commit()
        new_uid = c.lastrowid
        conn.close()

        # Log user in
        session.clear()
        session['user_id'] = new_uid
        session['username'] = username
        session['role'] = role
        session['org_name'] = org_name
        session['city'] = city

        flash(f"Account registered successfully as {role.capitalize()}! Welcome to the Smart Redistribution network.", "success")
        if role == 'donor':
            return redirect(url_for('donate'))
        elif role == 'recipient':
            return redirect(url_for('redistribution'))
        else:
            return redirect(url_for('admin_dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('index'))

# -------------------------------------------------------------
# 7. ADMIN DASHBOARD & MANAGEMENT
# -------------------------------------------------------------
@app.route('/admin')
@role_required('admin')
def admin_dashboard():
    conn = get_db_connection()
    c = conn.cursor()

    # All listings with donor details
    c.execute("""
        SELECT d.*, u.contact_person, u.email as donor_email
        FROM donations d
        LEFT JOIN users u ON d.donor_id = u.id
        ORDER BY d.created_at DESC
    """)
    all_donations = [dict(row) for row in c.fetchall()]

    # All redistribution requests with donation title
    c.execute("""
        SELECT r.*, d.food_title, d.quantity_kg, d.city as donation_city, d.status as donation_status
        FROM redistribution_requests r
        JOIN donations d ON r.donation_id = d.id
        ORDER BY r.created_at DESC
    """)
    all_requests = [dict(row) for row in c.fetchall()]

    # Registered users
    c.execute("SELECT id, username, email, role, org_name, contact_person, phone, city, created_at FROM users ORDER BY created_at DESC")
    all_users = [dict(row) for row in c.fetchall()]

    # Prediction runs history
    c.execute("""
        SELECT p.*, u.org_name
        FROM predictions_log p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 20
    """)
    predictions_history = [dict(row) for row in c.fetchall()]

    conn.close()
    metrics = get_dashboard_metrics()

    return render_template(
        'admin.html',
        donations=all_donations,
        requests=all_requests,
        users=all_users,
        predictions=predictions_history,
        metrics=metrics
    )

@app.route('/admin/update-donation-status', methods=['POST'])
@role_required('admin')
def update_donation_status():
    donation_id = request.form.get('donation_id', type=int)
    new_status = request.form.get('new_status')

    if donation_id and new_status in ['Available', 'Requested', 'Claimed', 'Redistributed', 'Cancelled']:
        conn = get_db_connection()
        conn.execute("UPDATE donations SET status = ? WHERE id = ?", (new_status, donation_id))
        conn.commit()
        conn.close()
        flash(f"Donation #{donation_id} status updated to '{new_status}'.", "success")
    else:
        flash("Invalid status update parameters.", "danger")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update-request-status', methods=['POST'])
@role_required('admin')
def update_request_status():
    request_id = request.form.get('request_id', type=int)
    new_status = request.form.get('new_status')

    if request_id and new_status in ['Pending', 'Approved', 'Completed', 'Rejected']:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE redistribution_requests SET status = ? WHERE id = ?", (new_status, request_id))
        
        # If request is completed, also mark donation as Redistributed
        if new_status == 'Completed':
            req = c.execute("SELECT donation_id FROM redistribution_requests WHERE id = ?", (request_id,)).fetchone()
            if req:
                c.execute("UPDATE donations SET status = 'Redistributed' WHERE id = ?", (req['donation_id'],))

        conn.commit()
        conn.close()
        flash(f"Redistribution request #{request_id} updated to '{new_status}'.", "success")
    else:
        flash("Invalid request status update parameters.", "danger")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reset-demo-data', methods=['POST'])
@role_required('admin')
def reset_demo_data():
    from seed_data import seed_database
    try:
        seed_database()
        flash("Demonstration database reset and seeded with initial records successfully!", "success")
    except Exception as e:
        flash(f"Error reseeding database: {e}", "danger")
    return redirect(url_for('admin_dashboard'))

# -------------------------------------------------------------
# 8. REST API ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/metrics')
def api_metrics():
    """Provides real-time aggregated metrics for charts."""
    return jsonify(get_dashboard_metrics())

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions from AJAX or external callers."""
    data = request.get_json() or {}
    try:
        res = predict_surplus(
            food_type=data.get('food_type', 'Cooked Meals'),
            event_type=data.get('event_type', 'College Canteen'),
            day_of_week=data.get('day_of_week', 'Friday'),
            weather_condition=data.get('weather_condition', 'Sunny/Mild'),
            quantity_prepared_kg=float(data.get('quantity_prepared_kg', 50)),
            meals_prepared=int(data.get('meals_prepared', 120)),
            expected_attendance=int(data.get('expected_attendance', 110)),
            meals_consumed=int(data.get('meals_consumed', 80)),
            historical_waste_rate=float(data.get('historical_waste_rate', 0.12))
        )
        return jsonify({'status': 'success', 'data': res})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/download-zip')
def download_zip():
    """Provides direct 1-click download of the complete project zip archive."""
    zip_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'food-waste-redistribution-system.zip')
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name='food-waste-redistribution-system.zip')
    return "Zip file not found. Please generate it first.", 404

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting EcoDine AI Flask Application on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
