from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
import jwt   ###로그인페이지에 추가된 패키지: pyjwt
import datetime
import hashlib

app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.ehdakrl.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

##### 토큰(로그인 확인)후 없으면 로그인 페이지, 있으면 메인 페이지로
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

#####로그인(로그인) 페이지 렌더
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

#####로그인확인 후 토큰 발급
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#####회원가입 페이지 렌더
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

##### 중복확인 api
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# @app.route('/signup')
# def signup():
#
#     return render_template("signup.html")

#####추천 리스트 페이지 렌더
@app.route('/recommendList')
def recommendList():

    return render_template("recommendList.html")

#####마이페이지 렌더
@app.route('/mypage')
def mypage():
    return render_template("mypage.html")







#####로그인(인덱스) 페이지 API
@app.route('/api/login', methods=['POST'])
def login():

    return jsonify("로그인 완료")

#####프로필 API
@app.route('/api/profile', methods=['POST'])
def profile():
    return jsonify({"프로필 편집 완료"})

#####마이페이지 API
@app.route('/api/mypage', methods=['GET'])
def mypage_get():
    return jsonify({"프로필, 개인 플레이 리스트 조회"})






if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)