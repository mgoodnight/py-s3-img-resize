class Config(object):
    DEBUG = False
    FLASK_PORT = 5001
    CONTENT_TO_EXTENSIONS = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif'
    }

class Development(Config):
    ENV = 'development'
    DEBUG = True
    AWS_REGION = 'us-west-1'
    S3_BUCKET = 'foobar-bucket'

class Production(Config):
    ENV = 'production'


env_configs = {
    'development': Development,
    'production': Production
}
