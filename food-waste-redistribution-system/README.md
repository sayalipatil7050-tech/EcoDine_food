# AI-Based Food Waste Prediction and Smart Redistribution System
### College Digital Thinking Project

**EcoDine AI** is a complete, modern, responsive full-stack web application designed to combat food waste in university dining halls, cafeterias, and restaurants. It bridges the gap between surplus food generators and verified hunger-relief NGOs and community kitchens using **Machine Learning Demand Prediction** and an **Algorithmic Smart Redistribution Engine**.

---

## 🌟 Key Features

1. **Home Page (`/`)**
   - High-impact sustainable design themed in emerald green, warm cream, pure white, and vibrant orange.
   - Project introduction and Digital Thinking objective highlights.
   - Real-time impact tickers (Kilograms diverted, meals saved, CO₂e greenhouse gas averted).
   - 1-Click Persona Demo switcher for fast evaluation.

2. **Impact Analytics Dashboard (`/dashboard`)**
   - Live metrics: Total listings, active available surplus (kg & meals), successfully redistributed volume, and carbon footprint reduction.
   - Interactive **Chart.js** visualizations:
     - Food Surplus Volume by Category (Doughnut Chart)
     - Redistribution Flow Tracking (Bar Chart: Available vs. Claimed vs. Redistributed)
   - Recent activity audit feed with real-time status badges.

3. **AI Food Waste Prediction Model (`/predict`)**
   - Powered by a trained **Scikit-Learn Random Forest Regressor**.
   - Inputs: Food category, dining venue type, day of week, weather conditions, batch prep weight, total meals, expected attendance, consumed meals, and historical baseline waste rate.
   - Outputs: Predicted surplus quantity (kg & meals), waste ratio %, risk level (Low, Moderate, High, Critical), and actionable operational recommendations.
   - Direct CTA: *"List This Surplus for Smart Donation"* pre-populates the donation form with one click.
   - Includes transparent academic disclaimers and ML model performance metrics ($R^2$ and RMSE).

4. **Surplus Food Donation (`/donate`)**
   - Complete donation submission form with dietary classifications (Vegetarian, Vegan, Non-Veg, Jain).
   - Storage handling specifications (Room Temperature, Cold-Chain Chilled, Hot Holding).
   - Preparation timestamp and safe-use expiry deadline.
   - Auto-prefill support from logged-in user profile or ML prediction results.
   - Saved directly to persistent SQLite database.

5. **Smart Redistribution Network (`/redistribution`)**
   - Live filterable grid of surplus food listings with keyword search and category filters.
   - **Smart Matching Algorithm (`matching.py`)**:
     - Evaluates Geographic Proximity (35 pts)
     - Capacity Alignment Ratio (25 pts)
     - Time-to-Expiry Urgency Factor (25 pts)
     - Storage Compatibility (15 pts)
   - Computes an algorithmic **Match Score (0-100%)** with priority badges (e.g. *95% Prime Match*).
   - Interactive Recipient Simulator switcher to show how match scores dynamically change based on recipient capacity and location.
   - Instant "Claim / Request Food" modal with vehicle dispatch coordinator details.

6. **Authentication & Role-Based Access Control (`/login`, `/register`)**
   - Three distinct user roles: **Donor**, **Recipient (NGO)**, and **Administrator**.
   - Secure password hashing using Werkzeug `generate_password_hash` & `check_password_hash`.
   - 1-Click Fast Login for evaluators to test all three roles effortlessly without typing credentials.

7. **Administrator Console (`/admin`)**
   - Tabbed surveillance console for all food listings, NGO claims, ML prediction audit logs, and registered users.
   - Real-time status update controls (Available, Requested, Claimed, Redistributed, Cancelled).
   - 1-Click *"Reset Demo Database"* button to restore fresh sample data anytime.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Modern CSS3 (CSS Grid & Flexbox, Custom Design System), Vanilla JavaScript |
| **Icons & Charts**| Font Awesome 6, Chart.js 4.4 |
| **Backend** | Python Flask 3.1 |
| **Database** | SQLite3 (`data/food_waste.db`) |
| **AI / Machine Learning** | Scikit-Learn 1.9 (`RandomForestRegressor`, `OneHotEncoder`, `StandardScaler`), NumPy, Joblib |
| **Security** | Werkzeug Password Hashing, Session Management |

---

## 📂 Project Structure

```
food-waste-redistribution-system/
│
├── app.py                  # Flask application routes, auth, APIs, and business logic
├── database.py             # SQLite schema initialization and metric aggregations
├── ml_model.py             # Scikit-learn data generator, RF model training & predictor
├── matching.py             # Smart Redistribution multi-factor matching algorithm
├── seed_data.py            # Comprehensive demonstration dataset generator
├── requirements.txt        # Python dependency manifest
├── README.md               # Complete project documentation and running guide
│
├── data/
│   └── food_waste.db       # Persistent SQLite database (auto-created on boot)
│
├── models/
│   └── food_waste_rf_model.joblib # Serialized trained ML Random Forest model
│
├── static/
│   ├── css/
│   │   └── style.css       # Complete sustainable-themed modern CSS design system
│   └── js/
│       ├── main.js         # Responsive navigation, modals, and client helpers
│       └── dashboard.js    # Chart.js visualization configurations
│
└── templates/
    ├── base.html           # Master layout with responsive navbar, flash alerts & footer
    ├── index.html          # Hero section, impact tickers, benefits, persona demo strip
    ├── dashboard.html      # Metrics cards, Chart.js graphs, recent activity log
    ├── predict.html        # ML waste prediction form, risk meter & recommendation
    ├── donate.html         # Food donation submission form with safe handling checklist
    ├── redistribution.html # Smart matching network grid & claim modal
    ├── login.html          # Login form with 1-click evaluator persona switcher
    ├── register.html       # Role-based registration form
    └── admin.html          # Central administrative surveillance & management panel
```

---

## 🚀 Installation & Running Guide (Windows)

### Prerequisites
- Python 3.10+ (Python 3.11, 3.12, 3.13, 3.14 supported)
- Windows PowerShell or Command Prompt

### Step 1: Open the Project Directory
In Windows PowerShell:
```powershell
cd "C:\Users\Shree\.gemini\antigravity\scratch\food-waste-redistribution-system"
```

### Step 2: Install Required Dependencies
Install the required packages using pip:
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Initialize Database & Train the Machine Learning Model
The database and model auto-generate automatically on startup, but you can run them directly to verify:
```powershell
# 1. Train the Scikit-Learn Model
python ml_model.py

# 2. Seed the SQLite Database with Demonstration Data
python seed_data.py
```

### Step 4: Run the Flask Application
Start the local server:
```powershell
python app.py
```

### Step 5: Open in Your Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 👥 Demonstration User Credentials

For easy presentation during your college viva or project review, you can use the **1-Click Quick Login** buttons on the Login page (`/login`) or enter these credentials:

| Role | Username | Password | Organization | Purpose |
|---|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Campus Sustainability Cell | Manage all listings, update claim statuses, reset demo data |
| **Food Donor** | `apex_canteen` | `donor123` | Apex University Central Canteen | Post cooked surplus batches, inspect donation status |
| **Food Donor** | `hostel_mess` | `donor123` | Hostel Dining Facility #3 | List dinner surplus with cold-chain requirement |
| **Recipient (NGO)** | `annapoorna_ngo` | `recipient123` | Annapoorna Hunger Relief (300 cap) | Browse matches, claim urgent food with insulated van |
| **Recipient (NGO)** | `hope_shelter` | `recipient123` | Hope Haven Night Shelter (150 cap) | View regional matches, coordinate evening pickup |

---

## 🎓 College Viva & Demonstration Walkthrough Script

When presenting this Digital Thinking project to professors or evaluators, follow this recommended walkthrough:

1. **Introduction on Home Page (`/`)**:
   - Point out the **Digital Thinking problem statement**: Disconnect between campus dining overproduction and local NGO hunger relief.
   - Show the **live impact metrics strip** (Kilograms diverted, meals rescued, CO₂e averted).

2. **Predict Food Waste (`/predict`)**:
   - Demonstrate the **Scikit-Learn Machine Learning Model**.
   - Input sample: *College Canteen*, *Friday*, *Rainy/Storm*, *Prepared Qty: 80 kg*, *Meals: 180*, *Expected: 170*, *Consumed: 110*.
   - Click **Compute Surplus Prediction**.
   - Show the predicted surplus (~28.5 kg / ~68 meals), the **High Risk Badge**, and the recommended action.
   - Click the button: *"List This Surplus for Smart Donation"*.

3. **Food Donation (`/donate`)**:
   - Notice how the predicted quantity and meal counts are **automatically carried over**!
   - Fill in contact details and safe deadline.
   - Submit the listing to save it to SQLite.

4. **Smart Redistribution Engine (`/redistribution`)**:
   - Point out the **Smart Match Score Badge** (e.g., *92% Match*).
   - Expand the *"View Match Factor Breakdown"* accordion to explain how the algorithm weighs **Distance, Recipient Capacity, Urgency, and Storage**.
   - Use the **"Simulate Recipient Match" dropdown** to switch between *Annapoorna Foundation (Cap: 300)* and *Sandhya Senior Care (Cap: 60)* to show how match scores adapt to recipient capacity.
   - Click **"Claim / Request Food"** to demonstrate the pickup vehicle dispatch modal.

5. **Analytics Dashboard (`/dashboard`)**:
   - Review the **Chart.js** category breakdown doughnut chart and status flow bar chart.
   - Highlight the **FAO environmental benchmark** (2.5 kg CO₂e saved per 1 kg food rescued).

6. **Admin Console (`/admin`)**:
   - Login as `admin` to show central governance, donation status updates, prediction audit logs, and the 1-click database reset option.

---

## 📜 Compliance & Academic Integrity
- **Disclaimer**: Food surplus predictions are statistical approximations generated by a trained Random Forest Regressor on simulated institutional dining patterns for academic evaluation.
- Aligned with **UN Sustainable Development Goals**:
  - **SDG 2**: Zero Hunger
  - **SDG 12**: Responsible Consumption & Production
  - **SDG 13**: Climate Action
