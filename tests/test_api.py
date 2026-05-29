import unittest
import json
import os
import sys

# Add current path to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Override Config SQLALCHEMY_DATABASE_URI BEFORE creating the app to force SQLite in-memory
from app.core.config import Config
Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

from app import create_app
from app.extensions import db

class TestHRMAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_risk_prediction_endpoint_unauthorized(self):
        # Without logging in, this should return a redirect or unauthorized (since it requires login and hr_required)
        response = self.client.get('/ai/employee/1/risk')
        self.assertIn(response.status_code, (401, 302))  # Accept JSON 401 or redirect 302

    def test_explain_endpoint_unauthorized(self):
        response = self.client.get('/ai/employee/1/explain')
        self.assertIn(response.status_code, (401, 302))

    def test_recommendation_endpoint_unauthorized(self):
        response = self.client.get('/ai/employee/1/recommendations')
        self.assertIn(response.status_code, (401, 302))

    def test_auth_login_validation_invalid_input(self):
        # Testing invalid payload structure for auth routes
        payload = {
            'username': '',
            'password': ''
        }
        response = self.client.post('/login', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Returns login page with errors

if __name__ == '__main__':
    unittest.main()
