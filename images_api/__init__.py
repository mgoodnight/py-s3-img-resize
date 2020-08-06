import os
import boto3
from flask import Flask, request, jsonify, abort
from PIL import Image
from io import BytesIO
from .config import env_configs


def create_app():
    app = Flask(__name__)
    app.config.from_object(env_configs[os.getenv('ENVIRONMENT')])

    @app.route("/image", methods=['POST'])
    def push_img_s3():
        """
        POST /image file=img1.png

        Returns JSON payload with two lists of S3 keys that were successful and ones that failed.

        parameters:
            - name: width
                in: query
                type: integer
                required: false
                description: Desired resize width of your image
            - name: height
                in: query
                type: integer
                required: false
                description: Desired resize height of your image
            - name: preserve
                in: query
                type: boolean
                required: false
                description: Creates an S3 object of the original image and appends '-orig' to the S3 key
            - name: append
                in: query
                type: boolean
                required: false
                description: Appends the dimensions to the S3 key. Example: foobar-250x250.png
        """
        width = int(request.args.get('width', 0))
        height = int(request.args.get('height', 0))
        preserve = request.args.get('preserve', False)
        append = request.args.get('append', False)

        img_store = request.files.get('file', None)

        if not img_store:
            return jsonify({'error': 'Missing image'}), 400

        keys_success = []
        keys_failed = []

        key_args = {'append': append}

        pil_orig = __pil_from_store(img_store)
        name_extension = __get_filename_and_extension(img_store)

        if not name_extension[1]:
            return jsonify({'error': 'Cannot determine image type'}), 400

        key_args['name_extension'] = name_extension

        if width or height:
            pil_resized = __resize_pil(pil_orig, [width, height])
            key_args['dimensions'] = pil_resized.size
            key_args['set_original'] = False

            gen_s3_key = __create_s3_key(**key_args)
            upload_result = __upload(
                pil_resized, name_extension[1], gen_s3_key)
            keys_success.append(
                gen_s3_key) if upload_result else keys_failed.append(gen_s3_key)

            if preserve:
                key_args['dimensions'] = pil_orig.size
                key_args['set_original'] = True

                gen_s3_key = __create_s3_key(**key_args)
                upload_result = __upload(
                    pil_orig, name_extension[1], gen_s3_key)
                keys_success.append(
                    gen_s3_key) if upload_result else keys_failed.append(gen_s3_key)
        else:
            key_args['dimensions'] = pil_orig.size
            key_args['set_original'] = preserve

            gen_s3_key = __create_s3_key(**key_args)
            upload_result = __upload(
                pil_orig, name_extension[1], gen_s3_key)
            keys_success.append(
                gen_s3_key) if upload_result else keys_failed.append(gen_s3_key)

        return jsonify({'success': keys_success, 'failure': keys_failed}), 201

    def __pil_from_store(img_store):
        """Create PIL Image object from buffer via FileStorage data

        Args:
            img_store (FileStorage): Wrapper for incoming Flask files

        Returns:
            PIL.Image: New PIL Image based off of incoming file data
        """
        return Image.open(BytesIO(img_store.read()))

    def __resize_pil(img, new_dimensions):
        """Get resized PIL Image based off another PIL Image

        If we get only a width or a height, we scale the other to maintain aspect ratio

        Args:
            img (PIL.Image): PIL Image to be resized
            new_dimensions (List): 2-item list containing width and height

        Returns:
            PIL.Image: Resized PIL Image
        """
        if not new_dimensions[0] and not new_dimensions[1]:
            return img

        for i in range(len(new_dimensions)):
            if not new_dimensions[i]:
                new_dimensions[i] = int(
                    (new_dimensions[i-1]/img.size[i-1]) * img.size[i])

        return img.resize(new_dimensions)

    def __get_filename_and_extension(img_store):
        """Derive or generate a filename and attempt to determine proper file extenstion

        Args:
            img_store (FileStorage): Wrapper for incoming Flask files

        Returns:
            tuple: 2-item tuple containing a filename and an extension (if we could derive one)
        """
        name_extension = os.path.splitext(img_store.filename)

        if not name_extension[1]:
            try:
                content_type = img_store.content_type

                if content_type:
                    extension = app.config.get('CONTENT_TO_EXTENSIONS').get(
                        img_store.content_type.lower(), '')

                name_extension = (name_extension[0], f'{extension}')
            except AttributeError:
                pass

        return (name_extension[0], name_extension[1].replace('.', ''))

    def __create_s3_key(**kwargs):
        """Create an S3 key

        Returns:
            string: Newly created key based off of kwargs
        """
        dimensions = kwargs.get('dimensions', ())
        name_extension = kwargs.get('name_extension', ())
        s3_key = name_extension[0]

        if kwargs.get('append', False):
            s3_key += '-' + 'x'.join(str(i) for i in dimensions)

        if kwargs.get('set_original', False):
            s3_key += '-orig'

        return f'{s3_key}.{name_extension[1]}'

    def __upload(img, extension, key):
        """Upload image to S3

        Args:
            img (PIL.Image): PIL Image who's data we will be uploading to S3
            extension (string): Image file extension
            key (string): S3 key

        Returns:
            boolean: Success or failure of the S3 upload
        """
        region = app.config.get('AWS_REGION', None)
        bucket = app.config.get('S3_BUCKET', None)
        extension_normalized = extension.upper() if extension != 'jpg' else 'JPEG'

        s3 = boto3.client('s3', region_name=region)

        buffer = BytesIO()
        img.save(buffer, extension_normalized)
        buffer.seek(0)

        s3_result = s3.put_object(Bucket=bucket, Key=key, Body=buffer)

        if s3_result['ResponseMetadata']['HTTPStatusCode'] != 200:
            return False

        return True

    return app
