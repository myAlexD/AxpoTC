import requests
import pandas as pd
from datetime import datetime
import pytz
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('aemet_client.log'), logging.StreamHandler()])

class AEMETClient:
    BASE_URL = "https://opendata.aemet.es/opendata/api/antartida/datos/fechaini/{}/fechafin/{}/estacion/{}"
    STATIONS = {
        "Estación Meteorológica Juan Carlos I": "89064",
        "Estación Meteorológica Gabriel de Castilla": "89070"
    }
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO) 

        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to logger
        self.logger.addHandler(ch)
        
    def get_data(self, start_datetime, end_datetime, station, time_aggregation=None):
        station_id = self.STATIONS.get(station)
        if not station_id:
            self.logger.error("Invalid station name. Choose from the predefined station names.")
            raise ValueError("Invalid station name. Choose from the predefined station names.")
        
        start_datetime_str = self._format_datetime(start_datetime)
        end_datetime_str = self._format_datetime(end_datetime)
        
        url = self.BASE_URL.format(start_datetime_str, end_datetime_str, station_id)
        headers = {'Authorization': f'Bearer {self.api_key}'}  
        
        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        self.logger.debug(f"Response Status Code: {response.status_code}")
        self.logger.debug(f"Response Content: {response.text}")
        
        if response.status_code == 401:
            self.logger.error("Unauthorized: Check your API key.")
            raise ValueError("Unauthorized: Check your API key.")
        if response.status_code == 404:
            self.logger.error("Not Found: Check the URL and parameters.")
            raise ValueError("Not Found: Check the URL and parameters.")
        if response.status_code == 429:
            self.logger.error("Too Many Requests: You have exceeded the rate limit.")
            raise ValueError("Too Many Requests: You have exceeded the rate limit.")
        
        response.raise_for_status()
        
        data_url = response.json().get('datos')
        if not data_url:
            self.logger.error("Failed to retrieve data URL from the API response.")
            raise ValueError("Failed to retrieve data URL from the API response.")
        
        data_response = requests.get(data_url)
        self.logger.debug(f"Response Status Code: {data_response.status_code}")
        self.logger.debug(f"Response Content: {data_response.text}")
        data_response.raise_for_status()
        
        data = data_response.json()
        
        df = self._process_data(data)
        df = self._convert_to_cet(df)
        
        if time_aggregation:
            df = self._aggregate_data(df, time_aggregation)
        
        return df
    
    def _format_datetime(self, dt):
        try:
            return dt.strftime('%Y-%m-%dT%H:%M:%SUTC')
        except Exception as e:
            self.logger.error(f"Error formatting datetime: {e}")
            raise ValueError(f"Error formatting datetime: {e}")
    
    def _process_data(self, data):
        try:
            records = []
            for entry in data:
                record = {
                    "Station": entry.get("nombre"),
                    "Datetime": entry.get("fhora"),
                    "Temperature (ºC)": entry.get("temp"),
                    "Pressure (hpa)": entry.get("pres"),
                    "Speed (m/s)": entry.get("vel")
                }
                records.append(record)
            
            df = pd.DataFrame(records)
            df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%dT%H:%M:%S%z')  # Handle timezone
            return df
        
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            raise ValueError(f"Error processing data: {e}")
    
    def _convert_to_cet(self, df):
        try:
            cet = pytz.timezone('CET')
            df['Datetime'] = df['Datetime'].dt.tz_convert(cet)
            return df
        
        except Exception as e:
            self.logger.error(f"Error converting to CET: {e}")
            raise ValueError(f"Error converting to CET: {e}")
    
    def _aggregate_data(self, df, aggregation):
        try:
            df.set_index('Datetime', inplace=True)
            numeric_cols = df.select_dtypes(include='number').columns
            
            if aggregation == 'Hourly':
                df_agg = df[numeric_cols].resample('H').mean().reset_index()
            elif aggregation == 'Daily':
                df_agg = df[numeric_cols].resample('D').mean().reset_index()
            elif aggregation == 'Monthly':
                df_agg = df[numeric_cols].resample('ME').mean().reset_index()
            else:
                df_agg = df.reset_index()
            
            return df_agg
        
        except Exception as e:
            self.logger.error(f"Error aggregating data: {e}")
            raise ValueError(f"Error aggregating data: {e}")

