from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.ehdakrl.mongodb.net/?retryWrites=true&w=majority')
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