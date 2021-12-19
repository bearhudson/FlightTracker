import requests
from src.environs import *
from dateutil import parser
from rich.table import Table
from rich.console import Console
from datetime import datetime
from datetime import timedelta

endpoint = "https://tequila-api.kiwi.com/v2/search"
headers = {
    "apikey": apikey,
}

search_dates = []
starting_at = '2022/03/03'
weeks = 5


def draw_table(params):
    request_api = requests.get(url=endpoint, params=params, headers=headers)
    request_api.raise_for_status()
    api_response_json = request_api.json()
    response_slice = api_response_json['data']

    city_from = response_slice[0]['flyFrom']
    city_to = response_slice[0]['flyTo']
    table = Table(f"Flight Tracker")
    console = Console()
    table.add_column("Price USD", justify="right", style="bright_red")
    table.add_column(f"Depart: {city_from}", justify="right", style="green")
    table.add_column(f"Return: {city_to}", justify="right", style="yellow")
    table.add_column(f"Airline", justify="right")
    table.add_column(f"Open Seats")

    for index in range(len(response_slice)):
        price = f"{response_slice[index]['price']}.00"
        departure = parser.parse(response_slice[index]['local_departure']).strftime('%m/%d at %H:%m')
        arrival = parser.parse(response_slice[index]['local_arrival']).strftime('%m/%d at %H:%m')
        airline = f"{response_slice[index]['airlines'][0]}"
        available = f"{response_slice[index]['availability']['seats']}"
        table.add_row(f"From {response_slice[0]['cityFrom']} to {response_slice[0]['cityTo']}",
                      price, departure, arrival, airline, available)
    console.print(table)


for index in range(weeks):
    start_date = datetime.strptime(starting_at, '%Y/%m/%d')
    search_date_start = (start_date + timedelta(weeks=index))
    search_date_start_string = search_date_start.strftime('%d/%m/%Y')
    search_date_end = (search_date_start + timedelta(days=2)).strftime('%d/%m/%Y')
    return_date_start = (start_date + timedelta(weeks=index + 2))
    return_date_start_string = return_date_start.strftime('%d/%m/%Y')
    return_date_end = (return_date_start + timedelta(days=2)).strftime('%d/%m/%Y')
    dest = [('BOS', 'YYC'), ('BOS', 'LHR'), ('BOS', 'NRT')]
    for d in dest:
        flight_params = {
            "fly_from": f"{d[0]}",
            "fly_to": f"{d[1]}",
            "date_from": f"{search_date_start_string}",
            "date_to": f"{search_date_end}",
            "curr": "USD",
            "selected_cabins": "M",
            "limit": 3
        }
        draw_table(flight_params)
        flight_params = {
            "fly_from": f"{d[1]}",
            "fly_to": f"{d[0]}",
            "date_from": f"{return_date_start_string}",
            "date_to": f"{return_date_end}",
            "curr": "USD",
            "selected_cabins": "M",
            "limit": 3
        }
        draw_table(flight_params)
