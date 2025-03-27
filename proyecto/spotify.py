import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Intentar cargar credenciales desde variables de entorno
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

# Si no se encuentran en variables de entorno, leer desde `credentials.txt`
if not client_id or not client_secret:
    try:
        with open("credentials.txt", "r") as f:
            credentials = f.read().splitlines()
            client_id = credentials[0].strip()
            client_secret = credentials[1].strip()
    except FileNotFoundError:
        raise ValueError("No se encontró el archivo 'credentials.txt' ni las credenciales en variables de entorno.")

# Validar que se hayan cargado las credenciales
if not client_id or not client_secret:
    raise ValueError("Las credenciales están vacías. Verifica 'credentials.txt'.")

# Autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

def get_artist_top_tracks(artist_name):
    """Obtiene el top 10 real del artista desde Spotify"""
    # Buscar el ID del artista
    result = sp.search(q=artist_name, type="artist", limit=1)
    if not result["artists"]["items"]:
        return ["No se encontró el artista"]

    artist_id = result["artists"]["items"][0]["id"]

    # Obtener las 10 canciones más populares del artista
    top_tracks = sp.artist_top_tracks(artist_id, country="US")["tracks"]
    
    # Ordenar las canciones de 10 a 1
    sorted_tracks = [f"{10 - idx}. {track['name']} - {track['artists'][0]['name']}" 
                     for idx, track in enumerate(reversed(top_tracks[:10]))]
    
    return sorted_tracks

def lambda_handler(event, context):
    """Función principal para AWS Lambda"""
    query = event.get("queryStringParameters", {}).get("artist", "")

    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "El parámetro 'artist' es requerido"})
        }

    top_songs = get_artist_top_tracks(query)

    return {
        "statusCode": 200,
        "body": json.dumps(top_songs, ensure_ascii=False)
    }

# Simulación para pruebas en Visual Studio Code
if __name__ == "__main__":
    while True:
        artist_name = input("Ingrese el nombre del artista (o escriba 'salir' para terminar): ")
        if artist_name.lower() == "salir":
            print("Programa finalizado.")
            break
        
        test_event = {"queryStringParameters": {"artist": artist_name}}
        response = lambda_handler(test_event, None)
        
        print("\nTop 10 canciones:\n")
        for song in json.loads(response["body"]):
            print(song)  # Cada canción se imprime en una línea separada
        print("\n----------------------------\n")
