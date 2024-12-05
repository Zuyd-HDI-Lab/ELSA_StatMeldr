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
