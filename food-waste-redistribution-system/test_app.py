import unittest
from app import app
from database import init_db, get_db_connection
from seed_data import seed_database

class EcoDineTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        seed_database()

    def setUp(self):
        self.client = app.test_client()

    def test_1_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EcoDine', response.data)
        self.assertIn(b'Predict Surplus', response.data)
        self.assertIn(b'Donate Food', response.data)

    def test_2_dashboard(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Food Waste & Redistribution Analytics', response.data)
        self.assertIn(b'categoryChart', response.data)
        self.assertIn(b'statusChart', response.data)

    def test_3_predict_get_and_post(self):
        # GET form
        res_get = self.client.get('/predict')
        self.assertEqual(res_get.status_code, 200)
        self.assertIn(b'Operational Parameters', res_get.data)

        # POST prediction with valid inputs
        res_post = self.client.post('/predict', data={
            'food_type': 'Cooked Meals',
            'event_type': 'College Canteen',
            'day_of_week': 'Friday',
            'weather_condition': 'Rainy/Storm',
            'quantity_prepared_kg': '70.0',
            'meals_prepared': '160',
            'expected_attendance': '150',
            'meals_consumed': '100',
            'historical_waste_rate': '0.12'
        })
        self.assertEqual(res_post.status_code, 200)
        self.assertIn(b'Surplus Food Forecast', res_post.data)
        self.assertIn(b'List This Surplus for Smart Donation', res_post.data)

    def test_4_food_donation_submission(self):
        res = self.client.post('/donate', data={
            'donor_name': 'Chef Test User',
            'org_name': 'Test College Canteen',
            'food_title': 'Unit Test Vegetable Pulao',
            'food_type': 'Cooked Meals',
            'quantity_kg': '20.0',
            'estimated_meals': '50',
            'prep_datetime': '2026-10-14 12:00',
            'expiry_datetime': '2026-10-14 18:00',
            'pickup_address': 'Test Campus Kitchen Dock 1',
            'city': 'Metro City',
            'contact_phone': '+91 99999 88888',
            'contact_email': 'test@campus.edu',
            'dietary_type': 'Vegetarian',
            'storage_requirement': 'Room Temperature',
            'notes': 'Unit test sample listing'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Unit Test Vegetable Pulao', res.data)

    def test_5_redistribution_and_matching(self):
        res = self.client.get('/redistribution')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Smart Redistribution Network', res.data)
        self.assertIn(b'% Match', res.data)

    def test_6_claim_food(self):
        # Fetch an available donation
        conn = get_db_connection()
        avail = conn.execute("SELECT id FROM donations WHERE status = 'Available' LIMIT 1").fetchone()
        conn.close()
        self.assertIsNotNone(avail)

        res = self.client.post('/claim-food', data={
            'donation_id': avail['id'],
            'recipient_org': 'Unit Test NGO',
            'contact_name': 'Test Coordinator',
            'contact_phone': '+91 98888 77777',
            'pickup_vehicle_type': 'Van / Mini-Truck',
            'beneficiary_count': '40',
            'estimated_pickup_time': '16:30',
            'request_notes': 'Arriving with insulated food boxes'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Claim successfully placed', res.data)

    def test_7_auth_and_admin(self):
        # Quick login as admin
        res_login = self.client.get('/quick-login/admin', follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Administrator Console', res_login.data)
        self.assertIn(b'surveillance of food donations', res_login.data)

if __name__ == '__main__':
    unittest.main()
