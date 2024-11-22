from django.shortcuts import render
import csv
import requests
from django.http import HttpResponse

def cbs_data(request):
    # Constant dataset ID
    dataset_id = "84583NED"
    url = f"https://opendata.cbs.nl/ODataApi/odata/{dataset_id}/TypedDataSet"

    # Haal het gemeente ID op uit de GET-parameter (standaard is Heerlen met ID '0917')
    gemeente_id = request.GET.get('gemeente', '0917')  # '0917' voor Heerlen en '0935' voor Maastricht

    # Parameters voor filtering en selectie
    params = {
        "$select": "WijkenEnBuurten,Gemeentenaam_1,AantalInwoners_5",
        "$filter": f"substring(WijkenEnBuurten,2,4) eq '{gemeente_id}'",
    }
    
    # Verzoek uitvoeren naar de CBS API
    response = requests.get(url, params=params)
    data = []
    if response.status_code == 200:
        data = response.json().get("value", [])
    else:
        print("Error:", response.status_code, response.text)

    # Render de HTML-template met de data
    return render(request, 'api/cbs_data.html', {'data': data})


def cbs_data_csv(request):
    # Constant dataset ID
    dataset_id = "84583NED"
    url = f"https://opendata.cbs.nl/ODataApi/odata/{dataset_id}/TypedDataSet"

    # Haal het gemeente ID op uit de GET-parameter
    gemeente_id = request.GET.get('gemeente', '0917')

    # Parameters voor filtering en selectie
    params = {
        "$select": "WijkenEnBuurten,Gemeentenaam_1,AantalInwoners_5",
        "$filter": f"substring(WijkenEnBuurten,2,4) eq '{gemeente_id}'",
    }
    
    # Verzoek uitvoeren naar de CBS API
    response = requests.get(url, params=params)
    data = response.json().get("value", []) if response.status_code == 200 else []

    # Maak een HTTP-respons voor het CSV-bestand
    csv_response = HttpResponse(content_type='text/csv')
    csv_response['Content-Disposition'] = 'attachment; filename="cbs_data.csv"'

    # Schrijf de data naar de CSV-respons
    if data:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_response, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return csv_response