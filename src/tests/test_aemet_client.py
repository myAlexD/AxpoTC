import unittest
from unittest.mock import patch, Mock
from datetime import datetime
import pandas as pd
from AxpoTC.src.aemet_client.aemet_client import AEMETClient  # Import your AEMETClient class

class TestAEMETClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key"
        self.client = AEMETClient(api_key=self.api_key)
        self.start_datetime = datetime(2023, 1, 1, 0, 0, 0)
        self.end_datetime = datetime(2023, 1, 10, 0, 0, 0)
        self.station = "Estación Meteorológica Gabriel de Castilla"

    def test_initialization(self):
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertIn(self.station, self.client.STATIONS)

    def test_invalid_station(self):
        with self.assertRaises(ValueError) as context:
            self.client.get_data(self.start_datetime, self.end_datetime, "Invalid Station")
        self.assertTrue('Invalid station name' in str(context.exception))

    @patch('requests.get')
    def test_unauthorized_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"descripcion": "API key invalido", "estado": 401}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.client.get_data(self.start_datetime, self.end_datetime, self.station)
        self.assertTrue('Unauthorized: Check your API key.' in str(context.exception))

    @patch('requests.get')
    def test_not_found_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"descripcion": "Not Found", "estado": 404}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.client.get_data(self.start_datetime, self.end_datetime, self.station)
        self.assertTrue('Not Found: Check the URL and parameters.' in str(context.exception))

    @patch('requests.get')
    def test_rate_limit_exceeded(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"descripcion": "Too Many Requests", "estado": 429}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.client.get_data(self.start_datetime, self.end_datetime, self.station)
        self.assertTrue('Too Many Requests: You have exceeded the rate limit.' in str(context.exception))

    @patch('requests.get')
    def test_successful_data_retrieval(self, mock_get):
        # Mock the first response to return the URL for data
        mock_initial_response = Mock()
        mock_initial_response.status_code = 200
        mock_initial_response.json.return_value = {
            "descripcion": "exito",
            "estado": 200,
            "datos": "https://opendata.aemet.es/opendata/sh/test_data_url"
        }

        # Mock the second response to return the actual data
        mock_data_response = Mock()
        mock_data_response.status_code = 200
        mock_data_response.json.return_value = [
            {
                "nombre": "GdC Estacion meteorologica",
                "fhora": "2023-01-07T00:00:00+0000",
                "temp": 4.7,
                "pres": 987.3,
                "vel": 9.3
            },
            {
                "nombre": "GdC Estacion meteorologica",
                "fhora": "2023-01-07T00:10:00+0000",
                "temp": 4.6,
                "pres": 987.6,
                "vel": 9.5
            }
        ]

        mock_get.side_effect = [mock_initial_response, mock_data_response]

        data = self.client.get_data(self.start_datetime, self.end_datetime, self.station)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 2)
        self.assertIn("Temperature (ºC)", data.columns)
        self.assertIn("Pressure (hpa)", data.columns)
        self.assertIn("Speed (m/s)", data.columns)

    @patch('requests.get')
    def test_aggregation(self, mock_get):
        # Mock the first response to return the URL for data
        mock_initial_response = Mock()
        mock_initial_response.status_code = 200
        mock_initial_response.json.return_value = {
            "descripcion": "exito",
            "estado": 200,
            "datos": "https://opendata.aemet.es/opendata/sh/test_data_url"
        }

        # Mock the second response to return the actual data
        mock_data_response = Mock()
        mock_data_response.status_code = 200
        mock_data_response.json.return_value = [
            {
                "nombre": "GdC Estacion meteorologica",
                "fhora": "2023-01-07T00:00:00+0000",
                "temp": 4.7,
                "pres": 987.3,
                "vel": 9.3
            },
            {
                "nombre": "GdC Estacion meteorologica",
                "fhora": "2023-01-07T01:00:00+0000",
                "temp": 4.6,
                "pres": 987.6,
                "vel": 9.5
            }
        ]

        mock_get.side_effect = [mock_initial_response, mock_data_response]

        data = self.client.get_data(self.start_datetime, self.end_datetime, self.station, time_aggregation='Hourly')
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 2)
        self.assertIn("Temperature (ºC)", data.columns)
        self.assertIn("Pressure (hpa)", data.columns)
        self.assertIn("Speed (m/s)", data.columns)

if __name__ == '__main__':
    unittest.main(verbosity=2)
