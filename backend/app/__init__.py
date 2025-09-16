from flask import Flask

def create_app():
    app = Flask(__name__)

    # 라우트 블루프린트 등록
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # 필요 시 여기서 DB, CORS, 로거, 설정 등 초기화
    # 예) from .database import init_db; init_db(app)

    return app
