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
    tickets = read_json('tickets_data.json')
    passengers = read_json('passengers_data.json')

    filtered_tickets = [ticket for ticket in tickets if ticket['flightNumber'] == int(flightNumber)]
    passenger_ids = {str(ticket['passengerID']) for ticket in filtered_tickets}

    # Crear un diccionario para mapear passengerID a seatNumber
    seat_map = {str(ticket['passengerID']): ticket['seatNumber'] for ticket in filtered_tickets}

    # Agregar seatNumber a los datos del pasajero
    flight_passengers = []
    for passenger in passengers:
        if passenger['passengerID'] in passenger_ids:
            passenger_with_seat = passenger.copy()
            passenger_with_seat['seatNumber'] = seat_map.get(passenger['passengerID'], 'N/A')
            flight_passengers.append(passenger_with_seat)

    return jsonify(flight_passengers)








