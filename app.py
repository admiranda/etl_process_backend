from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from utils.utils import read_json
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def ejecutar_main_py():
    # Ejecutar main.py como un proceso separado
    subprocess.run(["python", "main.py"])
    print("Ejecutando main.py")

scheduler = BackgroundScheduler()
scheduler.add_job(func=ejecutar_main_py, trigger="interval", minutes=20)
scheduler.start()


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
    seat_map = {str(ticket['passengerID']): ticket['seatNumber'] for ticket in filtered_tickets}

    flight_passengers = []
    for passenger in passengers:
        if passenger['passengerID'] in passenger_ids:
            passenger_with_seat = passenger.copy()
            passenger_with_seat['seatNumber'] = seat_map.get(passenger['passengerID'], 'N/A')
            flight_passengers.append(passenger_with_seat)

    # Ordenar los pasajeros por lastName antes de devolverlos
    flight_passengers.sort(key=lambda x: x['lastName'])

    return jsonify(flight_passengers)


if __name__ == '__main__':
    try:
        app.run(use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()






