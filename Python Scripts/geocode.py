import pandas as pd
from opencage.geocoder import OpenCageGeocode
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Load DF
df = pd.read_csv('../Data/scores.csv')

# Ensure the Location column exists
if 'Location' not in df.columns:
    raise ValueError("The DataFrame does not contain a 'Location' column.")

# Initialize the OpenCage geocoder with your API key
api_key = 'API KEY HERE'
geocoder = OpenCageGeocode(api_key)

# Function to get latitude and longitude with retry mechanism
def get_lat_long(location):
    retries = 3
    for i in range(retries):
        try:
            logger.info(f"Geocoding location: {location}, attempt {i+1}")
            result = geocoder.geocode(location, no_annotations='1', timeout=10)
            if result and len(result):
                logger.info(f"Geocoding successful for location: {location}")
                return result[0]['geometry']['lat'], result[0]['geometry']['lng']
            else:
                logger.warning(f"No result found for location: {location}")
                return None, None
        except Exception as e:
            logger.error(f"Error geocoding {location}: {e}")
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                return None, None

# Extract unique locations
unique_locations = df['Location'].unique()

# Create a dictionary to store the geocoded results
location_dict = {}

# Geocode each unique location
for location in unique_locations:
    lat, lng = get_lat_long(location)
    location_dict[location] = (lat, lng)

# Apply the geocoded results to the original DataFrame
df['Latitude'] = df['Location'].map(lambda loc: location_dict[loc][0])
df['Longitude'] = df['Location'].map(lambda loc: location_dict[loc][1])

# Write to a new .csv file
df.to_csv('../Data/geocoded_scores.csv', index=False)