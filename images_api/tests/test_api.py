def test_basic(client, flask_file_request_args):
    res = client.post('/image', **flask_file_request_args)
    assert res.status_code == 201
    assert res.get_json()['success'][0] == 'foobar.jpg'


def test_no_file(client):
    res = client.post('/image')
    assert res.status_code == 400
    assert res.get_json()['error'] == 'Missing image'


def test_no_extension(client, flask_file_no_extension):
    res = client.post('/image', **flask_file_no_extension)
    assert res.status_code == 400
    assert res.get_json()['error'] == 'Cannot determine image type'


def test_preserve(client, flask_file_request_args):
    res = client.post('/image?preserve=1&width=100', **flask_file_request_args)
    json = res.get_json()

    assert res.status_code == 201
    assert json['success'][0] == 'foobar.jpg'
    assert json['success'][1] == 'foobar-orig.jpg'


def test_append_resize(client, flask_file_request_args):
    res = client.post('/image?append=1&width=100&height=100', **flask_file_request_args)

    assert res.status_code == 201
    assert res.get_json()['success'][0] == 'foobar-100x100.jpg'


def test_preserve_resize(client, flask_file_request_args):
    res = client.post('/image?preserve=1&width=100&height=100', **flask_file_request_args)
    json = res.get_json()

    assert res.status_code == 201
    assert json['success'][0] == 'foobar.jpg'
    assert json['success'][1] == 'foobar-orig.jpg'
