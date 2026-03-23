import unittest
from io import BytesIO

from jaspr import app
from jaspr.model import JasprModel
from outlet import ParserRegistry


class TestLiveAppSurface(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_supported_parsers_are_exposed(self):
        expected = {
            'HINT celigo',
            'ICP celigo',
            'FRNT Virus-Serum-Serum Plate Layout Cx5',
            'FRNT Serum-Virus-Virus Plate Layout Cx5',
            'FRNT Virus-Serum-Serum Plate Layout Cytation7',
        }

        with app.test_request_context('/'):
            model = JasprModel()
            self.assertEqual(set(model.parser_list), expected)

        self.assertIn('anscombe', ParserRegistry.plugins)
        self.assertNotIn('hint_cx5', ParserRegistry.plugins)

    def test_upload_page_omits_legacy_parser(self):
        response = self.client.get('/upload')

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('HINT celigo', page)
        self.assertIn('ICP celigo', page)
        self.assertNotIn('hint_cx5', page)
        self.assertNotIn('Anscombe Quartet', page)

    def test_report_requires_loaded_analysis(self):
        response = self.client.get('/report')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/upload'))

    def test_empty_upload_redirects_to_error_page(self):
        response = self.client.post(
            '/upload',
            data={
                'datafile': (BytesIO(b''), ''),
                'keyfile': (BytesIO(b''), ''),
            },
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/error502'))

    def test_example_data_downloads_page_is_available(self):
        response = self.client.get('/downloadExampleData')

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('Example Data Downloads', page)
        self.assertIn('FRNT', page)
        self.assertIn('HINT', page)
        self.assertIn('ICP', page)


if __name__ == '__main__':
    unittest.main()