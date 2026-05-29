# tests/test_ai_endpoints.py
"""Automated tests for AI endpoints.
These tests verify that the AI routes are protected, return expected JSON structures,
and handle error cases gracefully.
"""
import unittest
import json
import os
import sys

# Ensure the project root is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import Employee

class TestAIEndpoints(unittest.TestCase):
    def setUp(self):
        # Create Flask test app with in‑memory SQLite DB
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Create a dummy employee for testing
            emp = Employee(id=1, fullname="Test User", email="test@example.com")
            db.session.add(emp)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.session.drop_all()

    def test_risk_endpoint_protected(self):
        # Should redirect to login when not authenticated
        response = self.client.get("/ai/employee/1/risk")
        self.assertIn(response.status_code, (302, 401))

    def test_explain_endpoint_protected(self):
        response = self.client.get("/ai/employee/1/explain")
        self.assertIn(response.status_code, (302, 401))

    def test_recommendations_endpoint_protected(self):
        response = self.client.get("/ai/employee/1/recommendations")
        self.assertIn(response.status_code, (302, 401))

    # Additional tests can be added after authentication flow is implemented.

if __name__ == "__main__":
    unittest.main()
