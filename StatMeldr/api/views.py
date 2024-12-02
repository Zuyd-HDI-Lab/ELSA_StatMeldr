from django.shortcuts import render
from django.http import HttpResponse
import csv
import redis
import json

def get_filtered_data(request):
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    # Haal de geselecteerde gemeente en jaar op
    selected_gemeente = request.GET.get('gemeente', 'Heerlen').strip()
    selected_jaar = request.GET.get('jaar', '2019')

    # Maak de sleutel met lowercase gemeente en jaar
    redis_key = f"kerncijfers:{selected_jaar}:{selected_gemeente.lower()}"
    print(f"Op te halen sleutel: {redis_key}")

    stored_data = redis_client.get(redis_key)

    # Controleer of data beschikbaar is
    if not stored_data:
        print(f"Geen data gevonden in Redis voor de sleutel: {redis_key}")
        return render(request, 'api/cbs_data.html', {
            'data': None,
            'gemeenten': sorted([
                k.decode().split(":")[2].capitalize()
                for k in redis_client.keys(f"kerncijfers:{selected_jaar}:*")
            ]),
            'jaren': sorted(set([
                k.decode().split(":")[1]
                for k in redis_client.keys("kerncijfers:*:*")
            ])),
            'selected_gemeente': selected_gemeente,
            'selected_jaar': selected_jaar,
        })

    # Decodeer de bytes naar een string en laad de JSON-data
    data = json.loads(stored_data.decode())

    return render(request, 'api/cbs_data.html', {
        'data': data,
        'gemeenten': sorted([
            k.decode().split(":")[2].capitalize()
            for k in redis_client.keys(f"kerncijfers:{selected_jaar}:*")
        ]),
        'jaren': sorted(set([
            k.decode().split(":")[1]
            for k in redis_client.keys("kerncijfers:*:*")
        ])),
        'selected_gemeente': selected_gemeente,
        'selected_jaar': selected_jaar,
    })


def get_filtered_data_csv(request):
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    # Haal de geselecteerde gemeente en jaar op uit de request
    selected_gemeente = request.GET.get('gemeente', 'heerlen').lower()
    selected_jaar = request.GET.get('jaar', '2019')

    # Op te halen sleutel in Redis
    redis_key = f"kerncijfers:{selected_jaar}:{selected_gemeente}"
    print(f"Op te halen sleutel voor CSV: {redis_key}")
    stored_data = redis_client.get(redis_key)

    # Controleer of data beschikbaar is
    if not stored_data:
        return HttpResponse("Geen data gevonden voor de geselecteerde gemeente en jaartal.", status=404)

    # Laad data en maak CSV-respons
    data = json.loads(stored_data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="kerncijfers_{selected_gemeente}_{selected_jaar}.csv"'

    # Schrijf data naar CSV
    if data:
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return response