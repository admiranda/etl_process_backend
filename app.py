from flask import Flask, jsonify, abort
import os
import json
from utils.utils import read_json

app = Flask(__name__)




@app.route('/')
def home():
    return "Hola, mundo!"

@app.route('/api/flights', methods=['GET'])
def get_flights():
    data = read_json('processed_data.json')
    return jsonify(data)

@app.route('/api/passengers', methods=['GET'])
def get_passengers():
    data = read_json('path/to/your/passengers.json')
    return jsonify(data)


