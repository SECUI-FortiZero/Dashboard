from flask import Flask
from flask_cors import CORS # [1. 수정] CORS 라이브러리 임포트

def create_app():
    # Flask 앱 객체 생성
    app = Flask(__name__)

    # [2. 수정] CORS 설정 추가
    # app 객체에 CORS를 적용합니다. 이러면 다른 출처(Origin)의 프론트엔드에서도 API를 호출할 수 있게 됩니다.
    CORS(app)

    # routes.py에서 bp 라는 이름의 Blueprint를 가져옵니다.
    from .routes import bp as main_bp
    
    # 앱에 Blueprint를 등록합니다. 이제 @bp.route로 정의된 모든 경로가 활성화됩니다.
    app.register_blueprint(main_bp)

    return app