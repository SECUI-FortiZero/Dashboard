from flask import Flask

def create_app():
    app = Flask(__name__)

    # test_api 블루프린트를 앱에 등록
    from .apis.test_api import test_bp
    app.register_blueprint(test_bp, url_prefix='/api')

    return app