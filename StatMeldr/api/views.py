from django.shortcuts import render
from django.http import HttpResponse
from io import StringIO
import pandas as pd
import csv
import redis
import json

def get_filtered_data(request):
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    selected_dataset = request.GET.get('dataset', 'kerncijfers').lower()
    selected_gemeente = request.GET.get('gemeente', 'heerlen').lower()
    selected_jaar = request.GET.get('jaar', '2019')

    redis_key = f"{selected_dataset}:{selected_jaar}:{selected_gemeente}"
    print(f"Op te halen sleutel: {redis_key}")
    stored_data = redis_client.get(redis_key)


    if not stored_data:
        return render(request, 'api/cbs_data.html', {
            'data': [],
            'gemeentes': [],
            'datasets': ['Kerncijfers', 'Uitkeringen'], 
            'selected_dataset': selected_dataset,
            'selected_jaar': selected_jaar,
            'selected_gemeente': selected_gemeente,
            'jaren': ['2019', '2020']
        })

    # Redis gebruikt bytes, je moet ze converteren naar een string format anders kan pandas er niks mee
    json_string = stored_data.decode('utf-8') 
    data = pd.read_json(StringIO(json_string), orient='records').to_dict(orient='records')


    gemeentes = redis_client.keys(f"{selected_dataset}:{selected_jaar}:*")
    gemeentes = sorted([key.decode().split(":")[-1].capitalize() for key in gemeentes])

    return render(request, 'api/cbs_data.html', {
        'data': data,
        'gemeentes': gemeentes,
        'datasets': ['Kerncijfers', 'Uitkeringen'], 
        'selected_dataset': selected_dataset,
        'selected_jaar': selected_jaar,
        'selected_gemeente': selected_gemeente.capitalize(),
        'jaren': ['2019', '2020']
    })

def get_rivm_data(request):
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    # Filters ophalen
    selected_gemeente = request.GET.get('gemeente', None)
    selected_period = request.GET.get('period', '2020JJ00')
    selected_age = request.GET.get('age', '20300')

    # Gemeentes ophalen uit Redis
    gemeentes = redis_client.keys(f"rivm:{selected_period}:{selected_age}:*")
    gemeentes = sorted([key.decode().split(":")[-1].capitalize() for key in gemeentes])

    if not gemeentes:
        return render(request, 'api/rivm_data.html', {
            'data': [],
            'gemeentes': [],
            'perioden': ['2020JJ00', '2022JJ00'],
            'leeftijden': ['20300', '53115', '80200'],
            'selected_gemeente': selected_gemeente,
            'selected_period': selected_period,
            'selected_age': selected_age,
        })

    # Als geen gemeente geselecteerd is, kies de eerste
    if not selected_gemeente or selected_gemeente.lower() not in [g.lower() for g in gemeentes]:
        selected_gemeente = gemeentes[0]

    # Redis-sleutel maken voor de geselecteerde filters
    redis_key = f"rivm:{selected_period}:{selected_age}:{selected_gemeente.lower()}"
    print(f"Op te halen sleutel: {redis_key}")

    # Data ophalen uit Redis
    stored_data = redis_client.get(redis_key)

    if stored_data:
        data = json.loads(stored_data)
    else:
        data = []

    # Periodes en leeftijden (vaste waarden)
    perioden = ['2020JJ00', '2022JJ00']
    leeftijden = ['20300', '53115', '80200']

    # Template renderen
    return render(request, 'api/rivm_data.html', {
        'data': data,
        'gemeentes': gemeentes,
        'perioden': perioden,
        'leeftijden': leeftijden,
        'selected_gemeente': selected_gemeente.capitalize(),
        'selected_period': selected_period,
        'selected_age': selected_age,
    })

#csv download functie
def get_filtered_data_csv(request): 
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    selected_gemeente = request.GET.get('gemeente', 'heerlen').lower()
    selected_jaar = request.GET.get('jaar', '2019')

    redis_key = f"kerncijfers:{selected_jaar}:{selected_gemeente}"
    print(f"Op te halen sleutel voor CSV: {redis_key}")
    stored_data = redis_client.get(redis_key)

    if not stored_data:
        return HttpResponse("Geen data gevonden voor de geselecteerde gemeente en jaartal.", status=404)


    full_data = json.loads(stored_data)

    filtered_data = [
        {key: row[key] for key in ["WijkenEnBuurten", "Gemeentenaam_1", "AantalInwoners_5"] if key in row}
        for row in full_data
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="kerncijfers_{selected_gemeente}_{selected_jaar}.csv"'

    if filtered_data:
        writer = csv.DictWriter(response, fieldnames=filtered_data[0].keys())
        writer.writeheader()
        writer.writerows(filtered_data)

    return response
