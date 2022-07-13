import re
import urllib
from flask import Flask, render_template, request, jsonify, redirect, url_for
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