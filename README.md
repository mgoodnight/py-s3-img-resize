
# ImagesAPI

Quick and easy API to push images to S3 that supports resizing and keeping copies of original images while all done in-memory

Good solution for your dev environments that needs to pump image assets to S3.

## Usage
 Set your bucket and region in `config.py`

`pip install -r requirements.txt`

`export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID>`

`export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>`

`export ENVIRONMENT=development`

`python app.py`

## Query params

`width`
Resize width. If no height query param is provided in conjunction, will scale based on aspect ratio.

`height`
Resize height. If no width query param is provided in conjunction, will scale based on aspect ratio.

`append`
Append dimensions to image(s). Example: `foobar-100x100.jpg`

`preserve`
If resizing (providing a width or a height query param), will create copy in S3 with `-orig` appended.

## Simple Recipes

### Basic upload image to S3

`curl -X POST -F file=@'/path/of/file/foobar.jpg' http://localhost:5001/image`

### Resize image to 100x100 and upload to S3

`curl -X POST -F file=@'/path/of/file/foobar.jpg' http://localhost:5001/image?height=100&width=100`

### Append dimensions to image object key and upload to S3

`curl -X POST -F file=@'/path/of/file/foobar.jpg' http://localhost:5001/image?append=1`

### Preserve original image and create 100x100 copy. Both uploaded to S3

`curl -X POST -F file=@'/path/of/file/foobar.jpg' http://localhost:5001/image?width=100&height=100&preserve=1`

## Tests
`ENVIRONMENT=development pytest`
