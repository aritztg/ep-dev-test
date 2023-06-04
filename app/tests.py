# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=import-error  # Because of potential circular import issue depending on pwd
import io
from os import getenv
from unittest import TestCase

import requests
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from PIL import Image

from app.simple_api import ATTRIBUTES_PATH, NDVI_PATH, THUMBNAILS_PATH, app

# Load env variables from `.env`.
load_dotenv()

# TestClient to be used for web app tests.
client = TestClient(app)

INVALID_CSRF_TOKEN = '123'
VALID_CSRF_TOKEN = getenv('VALID_CSRF_TOKEN')

# NDVI cannot executed outside the main thread because of Matplotlib. So testing NDVI_PATH require another approach.
ALL_PATHS_NO_NDVI = [ATTRIBUTES_PATH, THUMBNAILS_PATH]
ALL_PATHS = [ATTRIBUTES_PATH, THUMBNAILS_PATH, NDVI_PATH]

INPUT_FILE_PATH = 'input_data/S2L2A_2022-06-09.tiff'
input_file_handler = open(INPUT_FILE_PATH, 'rb')


class BackendSecurityTests(TestCase):

    def test_valid_token(self):
        for path in ALL_PATHS_NO_NDVI:
            input_file_handler.seek(0)
            response = client.post(path, params={'csrf_token': VALID_CSRF_TOKEN}, files={'image': input_file_handler})
            assert response.status_code == 200

    def test_no_token(self):
        input_file_handler.seek(0)
        for path in ALL_PATHS:
            response = client.post(path, timeout=10, params={}, files={'image': input_file_handler})
            assert response.status_code == 422

    def test_wrong_token(self):
        for path in ALL_PATHS:
            input_file_handler.seek(0)
            response = client.post(path,
                                   params={'csrf_token': INVALID_CSRF_TOKEN},
                                   files={'image': input_file_handler})

            assert response.status_code == 403
            assert response.json() == {'detail': 'Unauthorised. Invalid CSRF Token.'}

class ResponseTests(TestCase):

    def test_attributes_return(self):
        input_file_handler.seek(0)
        response = client.post(ATTRIBUTES_PATH,
                               params={'csrf_token': VALID_CSRF_TOKEN},
                               files={'image': input_file_handler})
        assert response.status_code == 200

        fields_to_check = ['width', 'height', 'bands', 'crs', 'bounds']

        # That is quite basic, ideally we would check also values types, or check all schema against a dataclass.
        for field in response.json():
            fields_to_check.remove(field)

        assert len(fields_to_check) == 0

    def test_thumbnails_return(self):
        input_file_handler.seek(0)
        response = client.post(THUMBNAILS_PATH,
                               params={'csrf_token': VALID_CSRF_TOKEN},
                               files={'image': input_file_handler})
        assert response.status_code == 200

        # Open response with PIL and confirm format (png) and size (hardcoded for now, 256x256).
        returned_image = Image.open(io.BytesIO(response.content))

        assert returned_image.format == 'PNG'
        assert returned_image.size == (256, 256)

    def test_ndvi_return(self):
        input_file_handler.seek(0)
        response = requests.post('http://0.0.0.0:80'+NDVI_PATH,
                                 timeout=10,
                                 params={'csrf_token': VALID_CSRF_TOKEN},
                                 files={'image': input_file_handler})
        assert response.status_code == 200

        # Open response with PIL and confirm format (png) and size (hardcoded for now, 1024x1024).
        returned_image = Image.open(io.BytesIO(response.content))

        assert returned_image.format == 'PNG'
        assert returned_image.size == (1024, 1024)
