#!/usr/bin/python3

import requests
from src.environs import *
from dateutil import parser
from rich.table import Table
from rich.console import Console
from rich.progress import track
from rich import print as pprint, box
from datetime import datetime
from datetime import timedelta
import time

endpoint = "https://tequila-api.kiwi.com/v2/search"
headers = {
    "apikey": apikey,
}

airport_list = ['YYC', 'STN', 'SEA', 'NRT', 'VCE',  'SIN', 'KUL', 'BKK', 'MNL']
home_airport = 'BOS'
search_dates = []
start_date = '2022/03/03'
weeks = 10
max_stopovers = 1
max_limit_returns = 3
weeks_traveling = 2


def draw_table(params):
    fly_from = ""
    fly_to = ""
    city_from = ""
    city_to = ""
    request_api = requests.get(url=endpoint, params=params, headers=headers)
    request_api.raise_for_status()
    api_response_json = request_api.json()
    response_slice = api_response_json['data']
    try:
        fly_from = response_slice[0]['flyFrom']
        fly_to = response_slice[0]['flyTo']
        city_from = response_slice[0]['cityFrom']
        city_to = response_slice[0]['cityTo']
    except IndexError as error:
        print("----- Error fetching data. Please verify parameters and try again.-----")

    table = Table(f"From {city_from} to {city_to}",
                  title_justify="center", box=box.MINIMAL_HEAVY_HEAD)
    console = Console()
    table.add_column("Price (USD)", style="bright_red", justify="right")
    table.add_column("Bag Price", justify="right")
    table.add_column(f"Depart: {fly_from}", style="sea_green2", justify="right")
    table.add_column(f"Arrive: {fly_to}", style="gold1", justify="right")
    table.add_column("Duration", style="deep_pink2", justify="right")
    table.add_column("Conn.", justify="right")
    table.add_column("Dist. (mi)", justify="right", style='gold3')
    table.add_column("Airline", justify="right")
    table.add_column("Open Seats", justify="right")
    table.add_column("URL", justify="right")

    for index in range(len(response_slice)):
        route_list = response_slice[index]['route']
        route_list_string = ""
        for route_count in range(len(route_list)):
            if route_count >= 1:
                route_list_string += " | "
            route_list_string += f"{route_list[route_count]['flyFrom']} -> {route_list[route_count]['flyTo']}"
        price = "{:,.2f}".format(response_slice[index]['price'])
        bag_price = "{:,.2f}".format(response_slice[index]['bags_price'].pop('1'))
        departure = parser.parse(response_slice[index]['local_departure']).strftime('%m/%d at %H:%m')
        arrival = parser.parse(response_slice[index]['local_arrival']).strftime('%m/%d at %H:%m')
        duration_seconds = response_slice[index]['duration']['total']
        duration_hms = time.strftime('%H:%M', time.gmtime(duration_seconds))
        connections = f"{len(response_slice[index]['route'])}"
        distance = f"{response_slice[index]['distance']}"
        airline = f"{response_slice[index]['airlines'][0]}"
        seats_available = f"{response_slice[index]['availability']['seats']}"
        deep_link = f"[link={response_slice[index]['deep_link']}]Link[/link]"
        table.add_row(f"{route_list_string}", price, bag_price, departure, arrival,
                      duration_hms, connections, distance, airline, seats_available, deep_link)
    console.print(table)


def get_flights(starting_at, from_airport, to_airport, span, currency, cabin):
    start_at = datetime.strptime(starting_at, '%Y/%m/%d')
    search_date_start = (start_at + timedelta(weeks=span))
    search_date_start_string = search_date_start.strftime('%d/%m/%Y')
    search_date_end = (search_date_start + timedelta(days=2)).strftime('%d/%m/%Y')
    return_date_start = (start_at + timedelta(weeks=span + 2))
    return_date_start_string = return_date_start.strftime('%d/%m/%Y')
    return_date_end = (return_date_start + timedelta(days=2)).strftime('%d/%m/%Y')
    flight_params = {
        "fly_from": f"{from_airport}",
        "fly_to": f"{to_airport}",
        "date_from": f"{search_date_start_string}",
        "date_to": f"{search_date_end}",
        "curr": f"{currency}",
        "selected_cabins": f"{cabin}",
        "max_stopovers": max_stopovers,
        "limit": max_limit_returns,
        # "flight_type": "round"
    }
    draw_table(flight_params)
    flight_params = {
        "fly_from": f"{from_airport}",
        "fly_to": f"{to_airport}",
        "date_from": f"{return_date_start_string}",
        "date_to": f"{return_date_end}",
        "curr": f"{currency}",
        "selected_cabins": f"{cabin}",
        "max_stopovers": max_stopovers,
        "limit": max_limit_returns,
        # "flight_type": "round"
    }
    draw_table(flight_params)


for i in airport_list:
    get_flights(starting_at=start_date, from_airport=home_airport, to_airport=i,
                span=weeks_traveling, currency='USD', cabin='M')
    get_flights(starting_at=start_date, from_airport=i, to_airport=home_airport,
                span=weeks_traveling, currency='USD', cabin='M')