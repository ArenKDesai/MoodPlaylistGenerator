from dotenv import load_dotenv
import os
from requests import post, get, put
import requests
import base64
import json
import numpy as np
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

def search_song(token, songName, limit=1):
    # From https://www.youtube.com/watch?v=WAmEZBEeNmg
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f'?q={songName}&type=track&limit=' + str(limit)
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

# Input: token, song in form of search_song(get_token(), songName)["tracks"]["items"][0]
def vectorize_song(token, song):
    songId = song["id"]
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
    return np.array(songVec)

def get_recommendation_vector(token, song_list):
    recVec = np.zeros(11)
    for song in song_list:
        songVec = vectorize_song(token, song)
        recVec += songVec
    recVec /= len(song_list)
    return recVec
        

def get_recommendations(token, song, limit=1):
    url = "https://api.spotify.com/v1/recommendations?limit=" + str(limit)
    headers = get_auth_header(token)
    songId = song["id"]
    songAcoustics = get_acoustics(token, songId)
    songVec = vectorize_song(token, song)
    songVec = [str(x) for x in songVec]
    songVec = ",".join(songVec)
    query = f'&seed_tracks={songId}&target_acousticness={songAcoustics["acousticness"]}&target_danceability={songAcoustics["danceability"]}&target_energy={songAcoustics["energy"]}&target_instrumentalness={songAcoustics["instrumentalness"]}&target_liveness={songAcoustics["liveness"]}&target_loudness={songAcoustics["loudness"]}&target_speechiness={songAcoustics["speechiness"]}&target_tempo={songAcoustics["tempo"]}&target_valence={songAcoustics["valence"]}'
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_next_song(token, basevec, user_song, listened_songs):
    recs = get_recommendations(token, user_song, 5)
    temporary_basevec = vectorize_song(token, user_song)
    best_song = None
    best_dist = None
    for song_rec in recs["tracks"]:
        second_recs = get_recommendations(token, song_rec, 5)
        for song in second_recs["tracks"]:
            if song["name"] in listened_songs:
                continue
            song_vec = vectorize_song(token, song)
            if(best_song == None or best_dist > np.linalg.norm(temporary_basevec - song_vec)):
                best_song = song
                best_dist = np.linalg.norm(temporary_basevec - song_vec)
    return best_song

def start_song(token, song):
    url = "https://api.spotify.com/v1/me/player/play"
    headers = get_auth_header(token)
    songUri = song["uri"]
    data = {"context_uri": songUri}
    result = put(url, headers=headers, json=data)
    json_result = json.loads(result.content)
    return json_result
    

if __name__ == '__main__':
    listened_songs = []
    songName = "Mr. Brightside"
    token = get_token()
    song = search_song(token, songName)["tracks"]["items"][0]
    print(start_song(token, song))