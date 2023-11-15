from flask import Flask, jsonify, abort
import os
import json
from utils.utils import read_json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)




@app.route('/')
def home():
    return "Hola, mundo!"

@app.route('/api/flights', methods=['GET'])
def get_flights():
    data = read_json('processed_data.json')
    return jsonify(data)

@app.route('/api/airports', methods=['GET'])
def get_airports():
    data = read_json('airports_data.json')
    return jsonify(data)

@app.route('/api/aircrafts', methods=['GET'])
def get_aircrafts():
    data = read_json('aircrafts_data.json')
    return jsonify(data)

@app.route('/api/passengers', methods=['GET'])
def get_passengers():
    data = read_json('passengers_data.json')
    return jsonify(data)





