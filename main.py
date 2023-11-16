import pandas as pd
import json
import os
import xml.etree.ElementTree as ET
import yaml
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import csv
from datetime import datetime
import locale

# Carga de datos
def clean_xml_file(file_path):
    with open(file_path, 'r+') as file:
        content = file.read()
        if not content.startswith('<root>') and not content.endswith('</root>'):
            content = '<root>' + content + '</root>'
        file.seek(0)
        file.write(content)
        file.truncate()

def preprocess_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r', newline='') as infile, open(output_file_path, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            # Esto une el tercer y cuarto elemento si hay más de 6 elementos.
            if len(row) > 6:
                row[2] = row[2] + ',' + row[3]
                del row[3]
            writer.writerow(row)

def cargar_datos_aeropuertos():
    # Preprocesar el archivo CSV antes de leerlo
    preprocess_csv('data/airports.csv', 'data/clean_airports.csv')
    airports_df = pd.read_csv('data/clean_airports.csv')
    return airports_df

def cargar_datos_aviones():
    clean_xml_file('data/aircrafts.xml')
    try:
        tree = ET.parse('data/aircrafts.xml')
        root = tree.getroot()
        # Procesamiento adicional aquí...
    except ET.ParseError as e:
        print(f'Error al parsear el archivo XML: {e}')
        return None
    
    tree = ET.parse('data/aircrafts.xml')
    root = tree.getroot()
    aircrafts = {'aircraftID': [], 'name': [], 'aircraftType': []}
    for aircraft in root.findall('row'):
        aircrafts['aircraftID'].append(aircraft.find('aircraftID').text)
        aircrafts['name'].append(aircraft.find('name').text)
        aircrafts['aircraftType'].append(aircraft.find('aircraftType').text)
    aircrafts_df = pd.DataFrame(aircrafts)
    return aircrafts_df

def cargar_datos_pasajeros():
    with open('data/passengers.yaml') as file:
        passengers_data = yaml.safe_load(file)
    passengers_df = pd.DataFrame(passengers_data['passengers'])

    # Configurar el locale para que reconozca los nombres de los meses en español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    passengers_df['age'] = passengers_df['birthDate'].apply(calcular_edad)

    return passengers_df

def cargar_datos_tickets():
    tickets_df = pd.read_csv('data/tickets.csv')
    return tickets_df

def calcular_edad(fecha_nacimiento):
    try:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%d de %B de %Y')
        hoy = datetime.now()
        return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    except ValueError:
        return None


# Función para leer los datos de los vuelos
def leer_datos_vuelos():
    flights_list = []
    for root, dirs, files in os.walk('data/flights'):
        for file in files:
            if file.endswith('flight_data.json'):
                with open(os.path.join(root, file)) as f:
                    flight_data_list = json.load(f)  # asumiendo que esto devuelve una lista
                    for flight_data in flight_data_list:  # iterar a través de cada vuelo
                        flight_data['year'] = root.split(os.sep)[-2]
                        flight_data['month'] = root.split(os.sep)[-1]
                        flights_list.append(flight_data)
    flights_df = pd.DataFrame(flights_list)
    return flights_df


# Integración de todos los datos

def integrar_datos():
    flights_df = leer_datos_vuelos()
    aircrafts_df = cargar_datos_aviones()
    airports_df = cargar_datos_aeropuertos()
    passengers_df = cargar_datos_pasajeros()
    tickets_df = cargar_datos_tickets()

    airports_df.to_json('airports_data.json', orient='records')
    passengers_df.to_json('passengers_data.json', orient='records')
    tickets_df.to_json('tickets_data.json', orient='records')
    aircrafts_df.to_json('aircrafts_data.json', orient='records')
    print(aircrafts_df)
    # Convertir passengerID a string en ambos DataFrames para asegurar consistencia
    tickets_df['passengerID'] = tickets_df['passengerID'].astype(str)
    passengers_df['passengerID'] = passengers_df['passengerID'].astype(str)
    print(passengers_df.head())  # Verificar la columna 'age'

    # Unimos tickets con pasajeros para obtener la edad
    tickets_passengers_df = pd.merge(tickets_df, passengers_df[['passengerID', 'age']], on='passengerID')
    print(tickets_passengers_df.head())  # Verificar las edades y las llaves de unión

    # Calculamos la edad promedio de los pasajeros por vuelo
    average_age_df = tickets_passengers_df.groupby('flightNumber')['age'].mean().reset_index()
    average_age_df['flightNumber'] = average_age_df['flightNumber'].astype(str)
    print(average_age_df.head())  # Verificar la edad promedio por vuelo
    # Unimos los vuelos con la edad promedio
    flights_df['flightNumber'] = flights_df['flightNumber'].astype(str)
    flights_df = pd.merge(flights_df, average_age_df, on='flightNumber', how='left')
    flights_df['age'] = flights_df['age'].round().astype('Int64')
    print(flights_df.head())  # Verificar la edad promedio por vuelo
    # Calculamos la cantidad de pasajeros por vuelo
    passenger_count_df = tickets_df.groupby('flightNumber').size().reset_index(name='passengerCount')
    passenger_count_df['flightNumber'] = passenger_count_df['flightNumber'].astype(str)

    # Unimos los vuelos con la cantidad de pasajeros
    flights_df = flights_df.merge(passenger_count_df, on='flightNumber', how='left')

    # Unimos los vuelos con los aviones y aeropuertos
    flights_df = flights_df.merge(aircrafts_df, on='aircraftID', how='left')
    flights_df = flights_df.merge(
        airports_df.rename(columns={'airportIATA': 'originIATA', 'name': 'originName'}),
        on='originIATA',
        how='left'
    )
    flights_df = flights_df.merge(
        airports_df.rename(columns={'airportIATA': 'destinationIATA', 'name': 'destinationName'}),
        on='destinationIATA',
        how='left'
    )

    # Asumiendo que se tiene una función 'calcular_distancia' que retorna la distancia entre dos puntos geográficos
    # flights_df['distance'] = flights_df.apply(
    #     lambda row: calcular_distancia(row['lat_x'], row['lon_x'], row['lat_y'], row['lon_y']), axis=1
    # )

    # Ordenamos los datos
    flights_df.sort_values(by=['year', 'month', 'flightNumber'], inplace=True)

    return flights_df


# Cargar los datos integrados
final_df = integrar_datos()
final_df.sort_values(by=['year', 'month', 'flightNumber'], inplace=True)
final_df.to_json('processed_data.json', orient='records')


"""
# Aplicación Dash
app = Dash(__name__)



app.layout = html.Div([
    dash_table.DataTable(
        id='tabla-vuelos',
        columns=[{"name": i, "id": i} for i in final_df.columns],
        data=final_df.to_dict('records'),
        page_size=15,  # paginación de 15 vuelos
        sort_action="native",  # habilita la clasificación
        sort_mode="multi",  # permite la clasificación multi-columna
        sort_by=[  # establece el orden por defecto
            {'column_id': 'year', 'direction': 'asc'},
            {'column_id': 'month', 'direction': 'asc'},
            {'column_id': 'flightNumber', 'direction': 'asc'}
        ],
        # Añade las siguientes líneas si deseas que la paginación y el orden puedan ser modificados por el usuario
        page_action='native',  # permite a los usuarios cambiar la paginación
        # sort_as_null=['year', 'month', 'flightNumber'],  # permite a los usuarios quitar el orden predeterminado
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

"""