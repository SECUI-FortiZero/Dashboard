from app import create_app
from dotenv import load_dotenv

load_dotenv()

# 애플리케이션 팩토리 함수를 호출하여 앱 객체를 가져옵니다.
app = create_app()

if __name__ == '__main__':
    # use_reloader=False 옵션을 추가합니다.
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)