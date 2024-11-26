from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
import redis
import csv

def get_filtered_data(request):
    try:
        # Redis-client configureren
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

        # Data ophalen uit Redis
        cached_data = redis_client.get('kerncijfers2019')
        if not cached_data:
            return render(request, 'api/cbs_data.html', {'data': []})

        # Omzetten van bytes naar string
        cached_data_str = cached_data.decode('utf-8')

        # Data laden in een Pandas DataFrame
        data_kerncijfers = pd.read_json(cached_data_str, orient='records')

        # Geselecteerde gemeente ophalen (standaard: 'Heerlen')
        selected_gemeente = request.GET.get('gemeente', 'Heerlen').strip()

        # Filteren op Gemeentenaam_1
        filtered_data = data_kerncijfers[
            data_kerncijfers['Gemeentenaam_1'].str.strip().str.lower() == selected_gemeente.lower()
        ][['WijkenEnBuurten', 'Gemeentenaam_1']]

        # Data omzetten naar een lijst van dicts
        data = filtered_data.to_dict(orient='records')

        return render(request, 'api/cbs_data.html', {'data': data})
    except Exception as e:
        return JsonResponse({'error': f'Er is een fout opgetreden: {e}'}, status=500)




def get_filtered_data_csv(request):
    """
    Haalt gefilterde data op uit Redis en retourneert deze als een CSV-bestand.
    """
    try:
        # Redis-client configureren
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

        # Ophalen van data uit Redis
        cached_data = redis_client.get('kerncijfers2019')
        if not cached_data:
            return JsonResponse({'error': 'Data niet gevonden in Redis'}, status=404)

        # Laden van data in een Pandas DataFrame
        data_kerncijfers = pd.read_json(cached_data, orient='records')

        # Filteren op Gemeentenaam_1 == "Heerlen" en alleen specifieke kolommen behouden
        filtered_data = data_kerncijfers[
            data_kerncijfers['Gemeentenaam_1'] == 'Heerlen'
        ][['WijkenEnBuurten', 'Gemeentenaam_1']]

        # HTTP-respons voor CSV-bestand
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'

        # Schrijf de gefilterde data naar het CSV-bestand
        filtered_data.to_csv(response, index=False)
        return response
    except Exception as e:
        return JsonResponse({'error': f'Er is een fout opgetreden: {e}'}, status=500)
