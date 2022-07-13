import re
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bs4 import BeautifulSoup
import certifi
ca = certifi.where()
import requests
app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.ehdakrl.mongodb.net/?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.dbsparta

#####로그인(인덱스) 페이지 렌더
@app.route('/')
def main():
    return render_template("index.html")

#####회원가입 페이지 렌더
@app.route('/signup')
def signup():

    return render_template("signup.html")

#####추천 리스트 페이지 렌더
@app.route('/recommendList')
def recommendList():

    return render_template("recommendList.html")

#####마이페이지 렌더
@app.route('/mypage')
def mypage():
    return render_template("mypage.html")







##########################################
#####임시 디비에 추가하는 페이지
@app.route('/tempInsertPage')
def tempPage():
    return render_template("tempInsertPage.html")
#####임시 디비에 추가하는 API
@app.route("/playlist", methods=["POST"])
def movie_post():
    url = request.form['url_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    setSelect = soup.select_one('#body-content > div.songlist-box > div.music-list-wrap > table > tbody')
    howmany = setSelect.select('tr.list')

    def no_space(text):
        text1 = re.sub('&nbsp; | &nbsp;|\n|\t|\r', '', text)
        text2 = re.sub('\n\n', '', text1)
        return text2
    number = 0
    for i in range(1, len(howmany)+1, 1):
        setTitle = setSelect.select_one(f'tr:nth-child({i}) > td.info > a.title.ellipsis').text
        singer = setSelect.select_one(f'tr:nth-child({i}) > td.info > a.artist.ellipsis').text
        number = number + 1
        image = "http:" + setSelect.select_one(f'tr:nth-child({i}) > td:nth-child(3) > a > img').get("src")
        title = no_space(setTitle)

        doc = {
            'title': title,
            'singer': singer,
            'number': number,
            'image': image,
            'like': 0
        }

        i = i + 1
        db.playlist.insert_one(doc)

    return jsonify({'msg':'저장 완료!'})

@app.route("/playlist", methods=["GET"])
def movie_get():
        playlist = list(db.playlist.find({}, {'_id': False}))
        return jsonify({'playlist':playlist})
##########################################



###### 좋아요 표시 API
@app.route('/api/like', methods=['POST'])
def like():
    num_receive = request.form['number_give']
    user_receive = request.form['user_give']

    doc = {
        'title_num':num_receive,
        'user':user_receive
    }

    db.likedb.insert_one(doc)

    like_content =list(db.likedb.find({'title_num':int(num_receive), 'user':user_receive}))

    return jsonify({'like_mark':like_content})

######  좋아요 취소 API
@app.route('/api/like_cancel', methods=['POST'])
def like_cancel():
    num_receive = request.form['number_give']
    user_receive = request.form['user_give']

    db.playlist1.deleteOne({'number':int(num_receive)},{'user':user_receive})

    return jsonify({'msg': '좋아요 취소'})





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

#####플레이 리스트 API
@app.route('/api/recommendList', methods=['GET'])
def playlist_get():

    return jsonify({"체크된 태그 달린 플레이 리스트 조회"})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

# ###########################################구분선 #########################################


import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

from pymongo import MongoClient

client = MongoClient("mongodb+srv://test:sparta@cluster0.bpwj4ks.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.oneweek


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


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


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    profile_name_receive = request.form['profile_name_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": profile_name_receive,                       # 프로필 이름
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/check_dup2', methods=['POST'])
def check_dup2():
    profile_name_receive = request.form['profile_name_give']
    exists = bool(db.users.find_one({"profile_name": profile_name_receive}))
    return jsonify({'result': 'success', 'exists': exists})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
