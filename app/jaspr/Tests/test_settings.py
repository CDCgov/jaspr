import copy
import json
import unittest
from io import BytesIO
from unittest.mock import patch

from flask import session

from jaspr import app
from jaspr.charts import JasprChart
from jaspr.model import JasprModel
from outlet import ParserRegistry


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def submit_settings(self, **overrides):
        values = {
            'show_fit': 'true',
            'blank_correction': 'true',
            'x_axis_type': 'log',
            'curr_function': 'robust_logistic4',
        }
        values.update(overrides)
        return self.client.post('/settings', data=values)

    def upload(self, parser):
        return self.client.post('/upload', data={
            'parser': parser,
            'datafile': (BytesIO(b'data'), 'data.csv'),
            'keyfile': (BytesIO(b'key'), 'key.xlsx'),
        })

    def parser_settings(self, name):
        parser = ParserRegistry.plugins[name]
        with app.test_request_context('/'):
            experiments = JasprModel().experiments
        if name.startswith('FRNT'):
            sera = ([], [], [], [], [], [], {})
            viruses = ([], [], [], [], [], [], [], [], [], {})
        else:
            sera = ([], [], {})
            viruses = ([], {})
        with patch.object(parser, '_get_sera', return_value=sera), \
                patch.object(parser, '_get_viruses', return_value=viruses), \
                patch.object(parser, '_get_all_experiments', return_value=experiments):
            return parser('key.xlsx', 'data.csv')()

    def test_settings_form_is_compact_and_submits_all_controls(self):
        page = self.client.get('/settings').get_data(as_text=True)
        self.assertIn('method="post" action="/settings"', page)
        self.assertIn('type="submit" class="btn btn-primary">Update', page)
        for field in ('show_fit', 'blank_correction', 'x_axis_type', 'curr_function'):
            self.assertIn(f'name="{field}"', page)
        self.assertIn('value="linear" selected', page)
        self.assertNotIn('Check Connection', page)
        self.assertNotIn('Execute Analysis', page)
        self.assertNotIn('jaspr-settings.js', page)
        form = page.split('<form method="post"', 1)[1].split('</form>', 1)[0]
        self.assertNotIn('<br', form)
        self.assertIn('col-md-4', page)

    def test_update_without_data_saves_without_starting_analysis(self):
        response = self.submit_settings()
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.location.endswith('/settings?updated=1'))
        with self.client.session_transaction() as state:
            self.assertFalse(state.get('analysis_ready', False))
            self.assertEqual(state['_pending_settings']['curr_function'], 'robust_logistic4')
            self.assertTrue(state['blank_correction'])
        page = self.client.get(response.location).get_data(as_text=True)
        self.assertIn('Settings saved for the next analysis.', page)
        self.assertIn('value="robust_logistic4" selected', page)
        self.assertIn('value="log" id="log" checked', page)

    def test_update_with_loaded_data_refreshes_analysis_and_preserves_data(self):
        self.client.get('/loadAnscombeData')
        with self.client.session_transaction() as state:
            before = json.loads(state['experiments'])
        response = self.submit_settings(x_axis_type='linear', curr_function='robust_linear')
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.location.endswith('/analysis'))
        self.assertEqual(self.client.get(response.location).status_code, 200)
        with self.client.session_transaction() as state:
            self.assertEqual(json.loads(state['experiments']), before)
            self.assertTrue(state['show_fit'])
            self.assertTrue(state['blank_correction'])
            self.assertEqual(state['curr_function'], 'robust_linear')
            self.assertNotIn('_pending_settings', state)
        with self.client.session_transaction() as state:
            saved = dict(state)
        with app.test_request_context('/'):
            session.update(saved)
            chart = JasprChart()
            self.assertEqual(chart.m.curr_function, 'robust_linear')
            self.assertTrue(chart.m.blank_correction)

    def test_unchecked_boxes_are_saved_as_false(self):
        self.client.get('/loadAnscombeData')
        self.submit_settings(show_fit='false', blank_correction='false')
        with self.client.session_transaction() as state:
            self.assertIs(state['show_fit'], False)
            self.assertIs(state['blank_correction'], False)
        self.client.post('/settings', data={'x_axis_type': 'linear', 'curr_function': 'linear'})
        with self.client.session_transaction() as state:
            self.assertIs(state['show_fit'], False)
            self.assertIs(state['blank_correction'], False)

    def test_invalid_settings_are_rejected_atomically(self):
        self.client.get('/settings')
        for invalid in (
            {'x_axis_type': 'invalid'},
            {'curr_function': 'invalid'},
        ):
            with self.subTest(invalid=invalid):
                response = self.submit_settings(**invalid)
                self.assertEqual(response.status_code, 400)
                self.assertIn('Choose a valid axis scale', response.get_data(as_text=True))
                with self.client.session_transaction() as state:
                    self.assertEqual(state['curr_function'], 'linear')
                    self.assertEqual(state['x_axis_type'], 'linear')
                    self.assertFalse(state['blank_correction'])
                    self.assertNotIn('_pending_settings', state)

    def test_each_parser_loads_homepage_defaults(self):
        expected = {
            'HINT celigo': (True, 'robust_logistic4'),
            'ICP celigo': (True, 'ICP_robust_logistic3'),
            'FRNT Virus-Serum-Serum Plate Layout Cx5': (False, 'logistic4'),
            'FRNT Serum-Virus-Virus Plate Layout Cx5': (False, 'logistic4'),
            'FRNT Virus-Serum-Serum Plate Layout Cytation7': (False, 'logistic4'),
        }
        for name, (blank_correction, function) in expected.items():
            with self.subTest(parser=name):
                settings = self.parser_settings(name)
                self.assertTrue(settings['show_fit'])
                self.assertEqual(settings['blank_correction'], blank_correction)
                self.assertEqual(settings['x_axis_type'], 'log')
                self.assertEqual(settings['curr_function'], function)
                with patch.dict(ParserRegistry.plugins, {
                    name: lambda *args: lambda: copy.deepcopy(settings),
                }):
                    response = self.upload(name)
                self.assertEqual(response.status_code, 302)
                with self.client.session_transaction() as state:
                    self.assertTrue(state['show_fit'])
                    self.assertEqual(state['blank_correction'], blank_correction)
                    self.assertEqual(state['x_axis_type'], 'log')
                    self.assertEqual(state['curr_function'], function)
                    self.assertEqual(state['curr_parser'], name)

    def test_pending_settings_override_next_upload_only(self):
        name = 'HINT celigo'
        settings = self.parser_settings(name)
        self.submit_settings(
            show_fit='false', blank_correction='false',
            x_axis_type='linear', curr_function='robust_linear',
        )
        with patch.dict(ParserRegistry.plugins, {
            name: lambda *args: lambda: copy.deepcopy(settings),
        }):
            self.upload(name)
            with self.client.session_transaction() as state:
                self.assertFalse(state['show_fit'])
                self.assertFalse(state['blank_correction'])
                self.assertEqual(state['x_axis_type'], 'linear')
                self.assertEqual(state['curr_function'], 'robust_linear')
                self.assertNotIn('_pending_settings', state)
            self.upload(name)
        with self.client.session_transaction() as state:
            self.assertTrue(state['show_fit'])
            self.assertTrue(state['blank_correction'])
            self.assertEqual(state['x_axis_type'], 'log')
            self.assertEqual(state['curr_function'], 'robust_logistic4')

    def test_pending_settings_apply_to_demo_and_reset_clears_them(self):
        self.submit_settings(x_axis_type='linear', curr_function='robust_linear')
        response = self.client.get('/loadAnscombeData')
        self.assertTrue(response.location.endswith('/analysis'))
        with self.client.session_transaction() as state:
            self.assertEqual(state['curr_function'], 'robust_linear')
            self.assertNotIn('_pending_settings', state)
        self.client.get('/reset')
        self.submit_settings()
        self.client.get('/reset')
        self.client.get('/loadAnscombeData')
        with self.client.session_transaction() as state:
            self.assertEqual(state['curr_function'], 'linear')
            self.assertFalse(state['blank_correction'])

    def test_incomplete_upload_does_not_consume_saved_settings(self):
        self.submit_settings(curr_function='robust_linear')
        response = self.client.post('/upload', data={})
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as state:
            self.assertEqual(state['_pending_settings']['curr_function'], 'robust_linear')


if __name__ == '__main__':
    unittest.main()
