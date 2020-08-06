
# Job Cloud Server

Quick and easy API to push images to S3 that supports resizing and keeping copies of original images and all done in-memory.

## Usage
`pip install -r requirements.txt`

`export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID>`
`export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>`
`export ENVIRONMENT=development`

`python app.py`

`curl -X POST -F file=@'/path/of/file/foobar.jpg' http://localhost:5001/image`

## Tests
`ENVIRONMENT=development pytest`
