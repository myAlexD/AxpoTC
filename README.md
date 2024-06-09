# AxpoTC

This repository contains a Python library for retrieving historical weather data from the AEMET (Spanish Meteorological Agency) for the study of building a new Wind Farm in Antarctica. The library provides an interface to easily retrieve and process the required AEMET data.

## Requirements

The objective of this project is to develop a Python library meeting the requirements below:

-	The plugin shall use the endpoint: “/api/antartida/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{identificacion}”. This endpoint is providing the timeseries of different measurements in the specified meteo station and in the specified time range.

- **Parameters**: The user shall be able to specify the following parameters:
  - API Key
  - Datetime Start with format `AAAA-MM-DDTHH:MM:SSUTC`
  - Datetime End with format `AAAA-MM-DDTHH:MM:SSUTC`
  - Meteo Measurement Station: From the API documentation, there are two possible selections:
    - `Meteo Station Gabriel de Castilla`
    - `Meteo Station Juan Carlos I`
  - Time Aggregation: Possible values shall be None, Hourly, Daily, and Monthly.

- **Granularity**: The granularity of the data from the API is in 10 minutes.
  - The output dataset shall be aggregated based on the user selection of the Time Aggregation field.
  - The output dataset shall not be aggregated when None is selected.

- **Output Dataset Fields**:

  | API Response Name | Dataset Field Name   | Description                   |
  |-------------------|----------------------|-------------------------------|
  | nombre            | Station              | Name of the station           |
  | fhora             | Datetime             | Date and time of the measurement |
  | temp              | Temperature (ºC)     | Temperature in º Celsius      |
  | pres              | Pressure (hpa)       | Pressure in hpa               |
  | vel               | Speed (m/s)          | Wind speed in m/s             |

- The Datetime field of the output dataset shall be in CET/CEST time zone.

## Installation

### Installing from the Distribution Files

You can install the library directly from the distribution files included in the `dist` folder.

1. Navigate to the `dist` directory:
    ```bash
    cd dist
    ```

2. Install the package using `pip`:
    ```bash
    pip install aemet_client-0.1.0-py3-none-any.whl
    # or
    pip install aemet_client-0.1.0.tar.gz
    ```

### Building the Library

To build the library from the source, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/myAlexD/AxpoTC.git
    cd AxpoTC
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Build the distribution files:
    ```bash
    python setup.py sdist bdist_wheel
    ```

This will create the distribution files in the `dist` directory.

## Usage

Here is an example of how to use the `AEMETClient` class to retrieve and process data:

```python
from datetime import datetime
from aemet_client import AEMETClient

# Initialize the client with your API key
api_key = "your_actual_api_key"
client = AEMETClient(api_key=api_key)

# Define parameters
start_datetime = datetime(2023, 1, 1, 0, 0, 0)
end_datetime = datetime(2023, 1, 10, 0, 0, 0)
station = "Meteo Station Gabriel de Castilla"
time_aggregation = "Daily"  # Options: None, Hourly, Daily, Monthly

# Retrieve and process data
try:
    data = client.get_data(start_datetime, end_datetime, station, time_aggregation)
    print(data)
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

```



## Tests

The library includes a comprehensive set of tests to cover various scenarios. The tests use the `unittest` framework and can be run using the `unittest` discovery mechanism.

### Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover
```
## License

This project is licensed under the MIT License.
