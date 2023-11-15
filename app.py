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

@app.route('/api/tickets/<flightNumber>', methods=['GET'])
def get_tickets_by_flight(flightNumber):
    all_tickets = read_json('tickets_data.json')
    tickets = [ticket for ticket in all_tickets if ticket['flightNumber'] == int(flightNumber)]
    return jsonify(tickets)

@app.route('/api/passengers/byflight/<flightNumber>', methods=['GET'])
def get_passengers_by_flight(flightNumber):
    # Cargar todos los tickets
    tickets = read_json('tickets_data.json')
    # Filtrar tickets por número de vuelo
    filtered_tickets = [ticket for ticket in tickets if ticket['flightNumber'] == int(flightNumber)]

    # Extraer los IDs de pasajeros de los tickets filtrados
    # Convertir a string para coincidir con los IDs en los datos de pasajeros
    passenger_ids = {str(ticket['passengerID']) for ticket in filtered_tickets}

    # Cargar todos los pasajeros
    passengers = read_json('passengers_data.json')
    # Filtrar los pasajeros que están en los tickets
    flight_passengers = [passenger for passenger in passengers if passenger['passengerID'] in passenger_ids]

    return jsonify(flight_passengers)







