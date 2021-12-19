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

search_dates = []
starting_at = '2022/03/03'
weeks = 5
# dest = [('BOS', 'YYC'), ('BOS', 'LHR'), ('BOS', 'NRT'), ('BOS', 'SEA')]
dest = [('BOS', 'LHR'), ('BOS', 'STN')]
max_stopovers = 1


def draw_table(params):
    request_api = requests.get(url=endpoint, params=params, headers=headers)
    request_api.raise_for_status()
    api_response_json = request_api.json()
    response_slice = api_response_json['data']

    city_from = response_slice[0]['flyFrom']
    city_to = response_slice[0]['flyTo']
    table = Table(f"From {response_slice[0]['cityFrom']} to {response_slice[0]['cityTo']}",
                  title_justify="left", box=box.MINIMAL_HEAVY_HEAD)
    console = Console()
    table.add_column("Price (USD)", style="bright_red", justify="right")
    table.add_column("Bag Price", justify="right")
    table.add_column(f"Depart: {city_from}", style="green", justify="right")
    table.add_column(f"Arrive: {city_to}", style="yellow", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Conn.", justify="right")
    table.add_column("Dist. (mi)", justify="right")
    table.add_column("Airline", justify="right")
    table.add_column("Open Seats", justify="right")

    for index in range(len(response_slice)):
        route_list = response_slice[index]['route']
        route_list_string = ""
        for route_count in range(len(route_list)):
            if route_count >= 1:
                route_list_string += " | "
            route_list_string += f"{route_list[route_count]['flyFrom']} -> {route_list[route_count]['flyTo']}"
        price = f"{response_slice[index]['price']}.00"
        bag_price = f"{response_slice[index]['bags_price'].pop('1')}"
        departure = parser.parse(response_slice[index]['local_departure']).strftime('%m/%d at %H:%m')
        arrival = parser.parse(response_slice[index]['local_arrival']).strftime('%m/%d at %H:%m')
        duration_seconds = response_slice[index]['duration']['total']
        duration_hms = time.strftime('%H:%M', time.gmtime(duration_seconds))
        connections = f"{len(response_slice[index]['route'])}"
        distance = f"{response_slice[index]['distance']}"
        airline = f"{response_slice[index]['airlines'][0]}"
        seats_available = f"{response_slice[index]['availability']['seats']}"
        table.add_row(f"{route_list_string}", price, bag_price, departure, arrival,
                      duration_hms, connections, distance, airline, seats_available)
    console.print(table)


for index in range(weeks):
    start_date = datetime.strptime(starting_at, '%Y/%m/%d')
    search_date_start = (start_date + timedelta(weeks=index))
    search_date_start_string = search_date_start.strftime('%d/%m/%Y')
    search_date_end = (search_date_start + timedelta(days=2)).strftime('%d/%m/%Y')
    return_date_start = (start_date + timedelta(weeks=index + 2))
    return_date_start_string = return_date_start.strftime('%d/%m/%Y')
    return_date_end = (return_date_start + timedelta(days=2)).strftime('%d/%m/%Y')
    for d in dest:
        flight_params = {
            "fly_from": f"{d[0]}",
            "fly_to": f"{d[1]}",
            "date_from": f"{search_date_start_string}",
            "date_to": f"{search_date_end}",
            "curr": "USD",
            "selected_cabins": "M",
            "max_stopovers": max_stopovers,
            "limit": 5
        }
        draw_table(flight_params)
        flight_params = {
            "fly_from": f"{d[1]}",
            "fly_to": f"{d[0]}",
            "date_from": f"{return_date_start_string}",
            "date_to": f"{return_date_end}",
            "curr": "USD",
            "selected_cabins": "M",
            "max_stopovers": max_stopovers,
            "limit": 5
        }
        draw_table(flight_params)
