from django.shortcuts import render
from django.http import HttpResponse
import csv
import redis
import json

def get_filtered_data(request):
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    selected_gemeente = request.GET.get('gemeente', 'Heerlen').strip()
    selected_jaar = request.GET.get('jaar', '2019')

    redis_key = f"kerncijfers:{selected_jaar}:{selected_gemeente.lower()}"
    print(f"Op te halen sleutel: {redis_key}") #debug print

    stored_data = redis_client.get(redis_key)

    if not stored_data: #data splitsen en opslaan in redis. 2 variabelen, jaartal : gemeente
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

    #redis data omzetten naar iets leesbaars. (redis doet alleen in bytes)
    full_data = json.loads(stored_data.decode())
    filtered_data = [
        {key: row[key] for key in ["WijkenEnBuurten", "Gemeentenaam_1", "AantalInwoners_5"] if key in row}
        for row in full_data
    ]

    return render(request, 'api/cbs_data.html', {
        'data': filtered_data,
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


def get_filtered_data_csv(request): #csv download
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
