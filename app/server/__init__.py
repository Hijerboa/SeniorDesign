import logging

from flask import Flask
from util.cred_handler import get_secret
from flask_swagger_ui import get_swaggerui_blueprint
from db.database_connection import initialize


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=get_secret('SECRET_KEY')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    initialize()

    app.logger.setLevel(logging.INFO)

    app.logger.info("Configuring Swagger")
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'CSP Auditing'
        }
    )

    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    
    app.logger.info("Registering blueprints")

    from . import user, twitter
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(twitter.bp, url_prefix='/twitter')

    return app
