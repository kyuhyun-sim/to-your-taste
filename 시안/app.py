from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
app = Flask(__name__)


from pymongo import MongoClient
client = MongoClient('13.125.53.163', 27017, username="test", password="1234")
db = client.dbsparta_playlist





@app.route('/')
def main():
    return render_template("main.html")


@app.route('/submain')
def submain():
    return render_template("submain.html")

@app.route("/movie", methods=["POST"])
def movie_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')['content']
    image = soup.select_one('meta[property="og:image"]')['content']
    desc = soup.select_one('meta[property="og:description"]')['content']

    doc = {
        'title': title,
        'image': image,
        'desc': desc,
        'star':star_receive,
        'comment':comment_receive,

    }
    db.movies.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)