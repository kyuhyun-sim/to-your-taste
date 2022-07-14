from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import certifi
import requests



app = Flask(__name__)
ca = certifi.where()
SECRET_KEY = 'SPARTA'

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

client = MongoClient('mongodb+srv://test:sparta@cluster0.ehdakrl.mongodb.net/?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.dbsparta




#####추천 리스트 페이지 렌더
@app.route('/recommendList')
def recommendList():

    return render_template("recommendList.html")

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
        setSong = soup.select_one(
            f'#body-content > div.songlist-box > div.music-list-wrap > table > tbody > tr:nth-child({i}) > td:nth-child(3) > a')
        test = setSong['onclick']
        songUrl = re.sub(r'[^0-9]', '', test)
        url = 'https://www.genie.co.kr/detail/albumInfo?axnm=' + songUrl

        doc = {
            'title': title,
            'singer': singer,
            'number': number,
            'image': image,
            'setUrl': url,
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


# ###########################################구분선 #########################################


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('tempInsertPage.html', user_info=user_info)

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



# ###########################################구분선 #########################################


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})



@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "date": date_receive
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1).limit(20))
        # 포스팅 목록 받아오기
        posts = list(db.posts.find({}).sort("date", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#좋아요 like table에 저장
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
