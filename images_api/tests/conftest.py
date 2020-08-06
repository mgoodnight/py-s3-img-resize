import pytest
from images_api import create_app
from io import BytesIO
import os

def request_args():
    with open(f'{os.getcwd()}/images_api/tests/images/unittests.jpg', 'rb') as img_bin:
        img = {'file': (BytesIO(img_bin.read()), 'foobar.jpg')}
        args = {'data': img, 'content_type': 'multipart/form-data'}

    return args

@pytest.fixture
def app(mocker):
    mocker.patch('botocore.client.BaseClient._make_api_call',
                 return_value={'ResponseMetadata': {'HTTPStatusCode': 200}})
    return create_app()

@pytest.fixture
def flask_file_request_args():
    return request_args()

@pytest.fixture
def flask_file_no_extension():
    arg_copy = request_args().copy()
    no_extension, _ = os.path.splitext(arg_copy['data']['file'][1])
    arg_copy['data']['file'] = (arg_copy['data']['file'][0], no_extension)

    return arg_copy
