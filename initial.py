# Imports
from dotenv import load_dotenv
import os
from requests import post, get
import base64
import json
load_dotenv()

def get_token():
    # From https://www.youtube.com/watch?v=WAmEZBEeNmg
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    # From https://www.youtube.com/watch?v=WAmEZBEeNmg
    return {"Authorization": "Bearer " + token}

def search_song(token, songName):
    # From https://www.youtube.com/watch?v=WAmEZBEeNmg
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f'?q={songName}&type=track&limit=1'
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_acoustics(token, songId):
    url = f"https://api.spotify.com/v1/audio-features/{songId}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def vectorize_song(token, songId):
    songAcoustics = get_acoustics(token, songId)
    songVec = []
    songVec.append(songAcoustics["danceability"])
    songVec.append(songAcoustics["energy"])
    songVec.append(songAcoustics["key"])
    songVec.append(songAcoustics["loudness"])
    songVec.append(songAcoustics["mode"])
    songVec.append(songAcoustics["speechiness"])
    songVec.append(songAcoustics["acousticness"])
    songVec.append(songAcoustics["instrumentalness"])
    songVec.append(songAcoustics["liveness"])
    songVec.append(songAcoustics["valence"])
    songVec.append(songAcoustics["tempo"])
    # Fields like duration_ms, time_signature, and id are not included
    return songVec

if __name__ == '__main__':
    songName = "Name of Love"
    songId = search_song(get_token(), songName)["tracks"]["items"][0]["id"]
    print(vectorize_song(get_token(), songId))