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

    selected_gemeente = request.GET.get('gemeente', None)
    selected_period = request.GET.get('period', '2020JJ00')
    selected_age = request.GET.get('age', '20300')

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

    if not selected_gemeente or selected_gemeente.lower() not in [g.lower() for g in gemeentes]:
        selected_gemeente = gemeentes[0]

    redis_key = f"rivm:{selected_period}:{selected_age}:{selected_gemeente.lower()}"
    print(f"Op te halen sleutel: {redis_key}")

    stored_data = redis_client.get(redis_key)
    if stored_data:
        data = json.loads(stored_data)
    else:
        data = []

    # static waarden. Wanneer je andere filters gaat gebruiken, pas dit aan.
    perioden = ['2020JJ00', '2022JJ00']
    leeftijden = ['20300', '53115', '80200']

    return render(request, 'api/rivm_data.html', {
        'data': data,
        'datasets': ['RIVM'],  # Alleen RIVM hier!!!
        'gemeentes': gemeentes,
        'selected_gemeente': selected_gemeente,
        'selected_periode': selected_period,
        'selected_leeftijd': selected_age,
        'perioden': ['2020JJ00', '2022JJ00'],
        'leeftijden': ['20300', '53115', '80200']
    })



def get_filtered_data_csv(request):
    print("De functie get_filtered_data_csv wordt aangeroepen")
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    selected_dataset = request.GET.get('dataset')
    selected_gemeente = request.GET.get('gemeente', '').lower()
    selected_jaar = request.GET.get('jaar', '')
    selected_periode = request.GET.get('perioden', '')
    selected_leeftijd = request.GET.get('leeftijd', '')

    if not selected_dataset or not selected_gemeente:
        return HttpResponse("Dataset of gemeente ontbreekt", status=400)

    if selected_dataset == 'rivm':
        redis_key = f"rivm:{selected_periode}:{selected_leeftijd}:{selected_gemeente}"
    else: 
        redis_key = f"{selected_dataset}:{selected_jaar}:{selected_gemeente}"

    print(f"Op te halen sleutel voor CSV: {redis_key}")
    stored_data = redis_client.get(redis_key)

    if not stored_data:
        return HttpResponse("Geen data gevonden voor de geselecteerde parameters.", status=404)


    full_data = json.loads(stored_data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_dataset}_{selected_gemeente}_{selected_jaar or selected_periode}.csv"'

    if full_data:
        writer = csv.DictWriter(response, fieldnames=full_data[0].keys())
        writer.writeheader()
        writer.writerows(full_data)

    return response
