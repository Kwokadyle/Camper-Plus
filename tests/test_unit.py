"""Unit Tests for Camper+ App"""

import unittest
import camperapp
from camperapp.models import db, CampEvent, CampGroup, Camper
import mock
from unittest.mock import patch, DEFAULT
from datetime import datetime


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = camperapp.app.test_client()
        self.app.application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.app = self.app.application
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_schedule_gets_schedule_template(self):
        """Test that the Schedule endpoint calls the schedule Page"""
        with patch.multiple('camperapp.routes', render_template=DEFAULT) as \
                mock_funcs:
            camperapp.routes.schedule()
            render_template = mock_funcs['render_template']
            self.assertTrue(render_template.called)
            call_args = render_template.call_args
            template_name = call_args[0][0]
            self.assertEqual(template_name, "schedule.html")

    def test_campers_gets_campers_template(self):
        """Test that the Schedule endpoint calls the schedule Page"""
        with patch.multiple('camperapp.routes', render_template=DEFAULT) as \
                mock_funcs:
            camperapp.routes.campers()
            render_template = mock_funcs['render_template']
            self.assertTrue(render_template.called)
            call_args = render_template.call_args
            template_name = call_args[0][0]
            self.assertEqual(template_name, "campers.html")

    def test_login_gets_login_template(self):
        """Test that the login route exists"""
        with patch.multiple("camperapp.routes", render_template=DEFAULT) as \
                mock_functions:
            camperapp.routes.login()
            render_template = mock_functions["render_template"]
            self.assertTrue(render_template.called)
            call_args = render_template.call_args
            file_name = call_args[0][0]
            self.assertEqual(file_name, "login.html")

    @mock.patch('camperapp.models.datetime')
    def test_CampEvent_convert_ISO_py_datetime(self, mock_datetime):
        ISO_datetime = "2017-10-10T12:25:27"
        self.assertTrue(camperapp.models.datetime is mock_datetime)
        CampEvent.convert_ISO_datetime_to_py_datetime(ISO_datetime)
        mock_datetime.strptime.assert_called_once_with(ISO_datetime, '%Y-%m-%dT%H:%M:%S')

    @patch.object(CampEvent, 'convert_ISO_datetime_to_py_datetime')
    def test_CampEvent_convert_calevent_to_campevent_args(self, mock_parser):
        full_cal_event = {
            'title': 'basketball',
            'start': '2017-10-10T12:00:05',
            'end': '2017-10-10T13:00:00',
            'group_id': '1'
        }

        campevent = CampEvent.convert_calevent_to_campevent(full_cal_event)
        mock_parser.assert_any_call(full_cal_event['start'])
        mock_parser.assert_any_call(full_cal_event['end'])

    def test_CampEvent_convert_calevent_to_campevent(self):
        full_cal_event = {
            'title': 'basketball',
            'start': '2017-10-10T12:00:05',
            'end': '2017-10-10T13:00:00',
            'group_id': '1'
        }

        campevent = CampEvent.convert_calevent_to_campevent(full_cal_event)
        self.assertEqual(campevent.title, full_cal_event['title'])
        self.assertTrue(campevent.start is not None)
        self.assertTrue(campevent.end is not None)
        self.assertEqual(campevent.group_id, int(full_cal_event['group_id']))

    def test_camper_save(self):
        name = 'daniel'
        age = 12
        camper = Camper(name, age)
        db.session.add(camper)
        db.session.commit()

        queried_camper = Camper.query.filter_by(name=name).one()
        self.assertTrue(queried_camper is not None)

    def test_campevent_save(self):
        title = "basketball"
        start = datetime.now()
        end = datetime.now()
        campevent = CampEvent(title, start, end)
        db.session.add(campevent)
        db.session.commit()

        queried_campevent = CampEvent.query.filter_by(title=title).one()
        self.assertTrue(queried_campevent is not None)

    def test_campgroup_save(self):
        name = 'falcons'
        color = 'yellow'

        campgroup = CampGroup(name, color)
        db.session.add(campgroup)
        db.session.commit()

        queried_campgroup = CampGroup.query.filter_by(name=name).one()
        self.assertTrue(queried_campgroup is not None)

    def test_campgroup_relationship(self):
        group_name = 'falcons'
        group_color = 'yellow'
        camper_name = 'daniel'
        camper_age = 12

        campgroup = CampGroup(group_name, group_color)
        camper = Camper(camper_name, camper_age)
        campgroup.campers.append(camper)
        db.session.add(campgroup)
        db.session.add(camper)
        db.session.commit()

        queried_campgroup = Camper.query.filter_by(name=camper_name).one()\
            .campgroup
        self.assertEqual(queried_campgroup, campgroup)

    def test_campevent_relationship(self):
        group_name = 'falcons'
        group_color = 'yellow'
        event_title = "basketball"
        event_start = datetime.now()
        event_end = datetime.now()

        campevent = CampEvent(event_title, event_start, event_end)
        campgroup = CampGroup(group_name, group_color)
        campgroup.events.append(campevent)
        db.session.add(campevent)
        db.session.add(campgroup)
        db.session.commit()

        queried_campgroup = CampEvent.query.filter_by(title=event_title).one().campgroup
        self.assertEqual(queried_campgroup, campgroup)
