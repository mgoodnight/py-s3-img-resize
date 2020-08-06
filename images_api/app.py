from images_api import create_app

if __name__ == '__main__':
    api = create_app()
    api.run(host="0.0.0.0", debug=api.config['DEBUG'], port=api.config['FLASK_PORT'])
