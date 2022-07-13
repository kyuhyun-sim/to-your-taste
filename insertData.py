from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.ehdakrl.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta


title = {'조금 이따 샤워해', 'The Journey To The West'}
singer ={'개리(feat.Crush)', 'Hisaishi Joe'}
image ={'static/images/조금 이따 샤워해 - 개리(feat.Crush).jpg','static/images/The Journey To The West - Hisaishi Joe.jpg'}
tag = {'운동','코딩'}


doc = {
    'title': title,
    'singer':singer,
    'image':image,
    'tag':tag
}


db.playlist.insert_one(doc)

