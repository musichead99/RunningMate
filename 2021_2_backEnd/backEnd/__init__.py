# __init__.py
from flask import Flask, jsonify
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError 
from test.test import Test
from user.register import Register
from user.login import Login
from user.logintest import LoginTest
from user.logout import Logout
from user.mail import Email, mail
import database, werkzeug.exceptions

app = Flask(__name__)
app.config.update(JWT_SECRET_KEY = "backendTest") # jwt encoding을 위한 secret key, 추후 수정 필요

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'testforcapstone@gmail.com'
app.config['MAIL_PASSWORD'] = 'testemail'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
jwt = JWTManager(app)
mail.init_app(app)
api = Api(
    app,
    version='test',
    title='2021_2_backend API Server',
    description='2021년 2학기 캡스톤디자인을 위한 API Server입니다.',
    term_url="/",
    contact="musichead99@naver.com"
    )

# request 유효성 체크 에러 메시지 처리
@app.errorhandler(InvalidRequestError)
def data_error(e):
    ReqErr = demo_error_formatter(e)[0]

    return jsonify({ "status" : "Failed", "message" : ReqErr['message']}), 400

# jwt_required 에러 메시지 처리
@jwt.unauthorized_loader
def unauthorized_token_callback_test(jwt_payload):
    return jsonify({"status" : "Failed", "message" : "Missing Authorization Header"}), 403

# jwt_required에 blcoklist checking기능 추가
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    db = database.DBClass()
    query = '''
        select * from revoked_tokens where jti=%s
    '''
    token = db.executeOne(query, (jti,))
    return token is not None

# 만료된 토큰으로 접근 시 반환할 메시지 처리
@jwt.revoked_token_loader
def revoked_token_response(jwt_header, jwt_payload):
    return jsonify({"status" : "Failed", "message" : "Token has been revoked"}),400

# 잘못된 메소드로 요청시 반환할 메시지 처리
@api.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def not_allowd_method(e):
    return {"status" : "Error", "message" : "The method is not allowed for the requested URL."},405

# namespace 등록
api.add_namespace(Test,'/')
api.add_namespace(Register,'/user')
api.add_namespace(Login, '/user')
api.add_namespace(LoginTest,'/user')
api.add_namespace(Logout,'/user')
api.add_namespace(Email,'/user')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug="true")