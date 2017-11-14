"""Integration Tests for Camper+ App"""

import unittest
import camperapp
import json


class TestUrls(unittest.TestCase):
    def setUp(self):
        self.app = camperapp.app.test_client()

    def test_home(self):
        """Test that home can be accessed"""
        response = self.app.get("/")
        self.assertTrue(response.status_code, 200)

    def test_calendar(self):
        """Test that the Calendar Page can be accessed"""
        response = self.app.get("/schedule")
        self.assertTrue(response.status_code, 200)

    def test_groups_on_schedule_page(self):
        """Test that the groups passed to the schedule page are all displayed"""
        json_data = {
            'title': 'Test Event',
            'start': '2017-8-8T12:00:00',
            'end': '2017-8-8T12:00:00',
            'group': '3'
        }

        response = self.app.post("/saveEvent", data=json.dumps(json_data), content_type='application/json')
        self.assertTrue(response.status_code, 200)
