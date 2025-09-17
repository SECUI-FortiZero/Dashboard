from flask import Blueprint, jsonify

# 'test'라는 이름의 블루프린트 생성
test_bp = Blueprint('test', __name__)

@test_bp.route('/hello', methods=['GET'])
def hello():
    """간단한 테스트용 API"""
    return jsonify({
        "status": "success",
        "message": "Hello from your new Flask Backend!"
    })
#확인용 주석