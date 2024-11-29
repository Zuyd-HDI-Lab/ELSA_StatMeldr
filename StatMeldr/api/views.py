from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
import redis
import json

def get_filtered_data(request):
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0) # verander dit naar IP en port van live server (wanneer live)

        keys = redis_client.keys('kerncijfers:*')
        gemeenten = sorted([key.decode('utf-8').split(':')[1].title() for key in keys]) #hier worden de gemeentenamen alftabetisch gezet, en wordt een Title Case toegepast

        selected_gemeente = request.GET.get('gemeente', gemeenten[0] if gemeenten else '').strip().lower()
        key = f"kerncijfers:{selected_gemeente}"

        print(f"Op te halen sleutel: {key}")

        cached_data = redis_client.get(key)
        if not cached_data:
            print("Geen data gevonden in Redis voor deze sleutel.")
            return render(request, 'api/cbs_data.html', {'data': [], 'gemeenten': gemeenten, 'selected_gemeente': selected_gemeente})


        json_data = json.loads(cached_data)
        filtered_data = [
            {key: item[key] for key in ['WijkenEnBuurten', 'Gemeentenaam_1', 'AantalInwoners_5']}
            for item in json_data
        ]

        return render(request, 'api/cbs_data.html', {
            'data': filtered_data,
            'gemeenten': gemeenten,
            'selected_gemeente': selected_gemeente
        })
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")
        return JsonResponse({'error': f'Er is een fout opgetreden: {e}'}, status=500)



def get_filtered_data_csv(request):
    """
    Haalt gefilterde data op uit Redis en retourneert deze als een CSV-bestand.
    """
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

        cached_data = redis_client.get('kerncijfers2019')
        if not cached_data:
            return JsonResponse({'error': 'Data niet gevonden in Redis'}, status=404)

        json_data = json.loads(cached_data)

        filtered_data = [
            {key: item[key] for key in ['WijkenEnBuurten', 'Gemeentenaam_1']}
            for item in json_data
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'

        filtered_data.to_csv(response, index=False)
        return response
    except Exception as e:
        return JsonResponse({'error': f'Er is een fout opgetreden: {e}'}, status=500)
