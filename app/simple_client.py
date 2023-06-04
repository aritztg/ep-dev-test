from os import getenv, makedirs
from pprint import pprint as pp

import requests
from dotenv import load_dotenv

# Load env variables from `.env`.
load_dotenv()

API_URL = 'http://0.0.0.0:80'
ATTRIBUTES_URL = f'{API_URL}/attributes/'
THUMBNAILS_PATH = f'{API_URL}/thumbnails/'
NDVI_PATH = f'{API_URL}/ndvi/'
INPUT_FILE_PATH = 'input_data/S2L2A_2022-06-09.tiff'
OUTPUT_PATH = 'output'
OUTPUT_THUMBNAIL_FILENAME = f'{OUTPUT_PATH}/output_thumbnail.png'  # It would be better to use os.path.join() here.
OUTPUT_NDVI_FILENAME = f'{OUTPUT_PATH}/output_ndvi.png'


if __name__ == '__main__':
    # Open file and get a valid CSRF token (mocked).

    with open(INPUT_FILE_PATH, 'rb') as input_file_handler:
        csrf_token = getenv('VALID_CSRF_TOKEN')

        # Send it to the API to retrieve its attributes.
        response = requests.post(ATTRIBUTES_URL,
                                timeout=10,
                                params={'csrf_token': csrf_token},
                                files={'image': input_file_handler})
        pp(response.json())

        # Send it to the API to retrieve it as resized PNG.
        input_file_handler.seek(0)
        response = requests.post(THUMBNAILS_PATH,
                                timeout=10,
                                params={'csrf_token': csrf_token},
                                files={'image': input_file_handler})
        makedirs(OUTPUT_PATH, exist_ok=True)
        with open(OUTPUT_THUMBNAIL_FILENAME, 'wb') as f:
            f.write(response.content)
            print(f'Thumbnail successfully written in {OUTPUT_THUMBNAIL_FILENAME}.')

        # Send it to the API to retrieve its computed ndvi.
        input_file_handler.seek(0)
        response = requests.post(NDVI_PATH,
                                timeout=10,
                                params={'csrf_token': csrf_token},
                                files={'image': input_file_handler})
        with open(OUTPUT_NDVI_FILENAME, 'wb') as f:
            f.write(response.content)
            print(f'Thumbnail successfully written in {OUTPUT_NDVI_FILENAME}.')
