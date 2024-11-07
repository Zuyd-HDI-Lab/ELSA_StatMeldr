from django.shortcuts import render
import requests

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