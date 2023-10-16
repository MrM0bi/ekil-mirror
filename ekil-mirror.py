#!/usr/bin/env python3
from datetime import datetime as dt
import requests
import json
import os


DATEFORMAT = "[%d/%m/%Y - %H:%M:%S] "

BOTTOKEN = os.getenv("TGB_MRMOBOT")
ALERTCHATID = os.getenv("TGC_OCLT_ALERT")

DATADIR = os.getenv("SF_DATADIR")
IDSECRETFN = os.getenv("SF_IDSECRETFN")
REFRESHTOKENFN = os.getenv("SF_REFRESHTOKENFN_MRMOBI")
CURRENTACCESSTOKENFN = os.getenv("SF_CURRENTACCESSTOKENFN_MRMOBI")

ACCOUNTAPIROOT = "https://accounts.spotify.com"
APIROOT = "https://api.spotify.com/v1"

LIKEMIRRORPLAYLISTID = os.getenv("SF_LIKEMIRRORPLAYLISTID_MRMOBI")



# Send an Alert to my Telegram Alert-Group
def telegramAlert(message):
    date = str(dt.now().strftime(DATEFORMAT))
    text = date+message
    requests.post(url="https://api.telegram.org/{0}/sendMessage?chat_id={1}&text=ekiL-Mirror: \n".format(BOTTOKEN, ALERTCHATID) + str(text))


# Refreshes the Access Token and returns it. The imput values stay the same.
def refreshAccessToken(idsecret64, refresh_token):

    url = f"{ACCOUNTAPIROOT}/api/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {idsecret64}"
    }

    body = {
        "grant_type": "refresh_token",
        "refresh_token": f"{refresh_token}"
    }

    res = requests.post(url=url, headers=headers, data=body)

    if res.ok:
        try:
            jres = json.loads(res.text)
        except Exception:
            text = "[ERROR] Unable to handle the response from refreshing the Access Token"
            print(text)
            telegramAlert(text)
            quit(-1)

        access_token = jres["access_token"]

        return access_token
    
    else:
        return None


# Test if we are able to access the "personal section", mostly to see if the access token is still valid
def testAccess(access_token):

    url = f"{APIROOT}/me"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(url=url, headers=headers)

    return res


# Get one page of my currently liked songs and return a stripped down list
def getSavedSongs(access_token, offset=0, limit=20):

    url = f"{APIROOT}/me/tracks?offset={offset}&limit={limit}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(url=url, headers=headers)

    if res.ok:
        try:
            jres = json.loads(res.text)
        except Exception:
            text = "[ERROR] Unable to handle the resonse from getting my saved songs"
            print(text)
            telegramAlert(text)
            quit(-1)

        stripped_list = []
        
        for track in jres["items"]:

            # Values to save
            track_stripped = {
                "uri": track["track"]["uri"],
                "name": track["track"]["name"],
                "added": track["added_at"]
            }

            stripped_list.append(track_stripped)

        return stripped_list

    else:
        return None


# Get all liked songs and return a stripped down list
def getAllSavedSongs(access_token):
    
    offset = 0
    limit = 50
    saved_songs = []

    while offset is not None:
        song_page = getSavedSongs(access_token, offset, limit)

        if len(song_page) > 0:
            saved_songs.extend(song_page)
            offset += limit
        else:
            offset = None

    return saved_songs


# Get one page of songs of a specific playlist and return a stripped down list
def getPlaylistItems(access_token, playlist_id, fields, offset=0, limit=20):

    url = f"{APIROOT}/playlists/{playlist_id}/tracks?fields={fields}&offset={offset}&limit={limit}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(url=url, headers=headers)

    if res.ok:
        try:
            jres = json.loads(res.text)
        except Exception:
            text = "[ERROR] Unable to handle the resonse from getting my saved songs"
            print(text)
            telegramAlert(text)
            quit(-1)

        stripped_list = []
        
        for track in jres["items"]:

            # Values to save
            track_stripped = {
                "uri": track["track"]["uri"],
                "name": track["track"]["name"],
                "added": track["added_at"]
            }

            stripped_list.append(track_stripped)

        return stripped_list

    else:
        return None


# Get all songs of a specific playlist and return a stripped down list
def getAllPlaylistItems(access_token, playlist_id, fields):
    
    offset = 0
    limit = 50
    playlist_items = []

    while offset is not None:
        song_page = getPlaylistItems(access_token, playlist_id, fields, offset, limit)

        if len(song_page) > 0:
            playlist_items.extend(song_page)
            offset += limit
        else:
            offset = None

    return playlist_items


# Adds a list of Tracks to a specific playlist
def addTracksToPlaylist(access_token, playlist_id, track_uris):
    position = 0
    url = f"{APIROOT}/playlists/{playlist_id}/tracks?position={position}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    tracks = {}
    tracks["uris"] = track_uris
    body = json.dumps(tracks)

    res = requests.post(url=url, headers=headers, data=body)

    if not res.ok:
        text = "[ERROR] Unable to add unsynced Tracks to the Likes-Mirror Playlist"
        print(text)
        telegramAlert(text)
        quit(-1)

    return res




##### START ###############


idsecret64 = refresh_token = current_access_token = ""

print("--- "+str(dt.now().strftime(DATEFORMAT))+"---")

# Getting all the required Tokens and secret
try:
    # Get clientid-clientsecret string
    with open(f"{DATADIR}{IDSECRETFN}", "r") as f:
        idsecret64 = "".join(f.readlines()).strip()

    # Get Refresh Token for user
    with open(f"{DATADIR}{REFRESHTOKENFN}", "r") as f:
        refresh_token = "".join(f.readlines()).strip()

    # Get current Access Token
    with open(f"{DATADIR}{CURRENTACCESSTOKENFN}", "r") as f:
        current_access_token = "".join(f.readlines()).strip()

    print("- Loaded Tokens and secret.")

except Exception:
        text = "[ERROR] Unable read required Tokens and secret"
        print(text)
        telegramAlert(text)
        quit(-1)



# Checks if the Token is still valid and renews it if needed
print("- Checking access... ", end="")
access = testAccess(current_access_token)
if not access.ok:
    current_access_token = refreshAccessToken(idsecret64, refresh_token)

    try:
        # Overwrite currently saved Access Token with the new one
        with open(f"{DATADIR}{CURRENTACCESSTOKENFN}", "w") as f:
            f.write(current_access_token)
    except Exception:
        text = "[ERROR] Unable to write new Access-Token to file"
        print(text)
        telegramAlert(text)
        quit(-1)

    print(f"\n   > Access Token refreshed. Written new Token to \"{DATADIR}{CURRENTACCESSTOKENFN}\"")
else:
    print(f"ok")




# Get a list of all saved songs of the user
# Example Result first value: {'uri': 'spotify:track:5A4Le7DS4KXVzC9gH5QRAh', 'name': 'God', 'added': '2023-10-09T18:04:49Z'}
print("- Getting Saved Songs... ", end="")
saved_songs = getAllSavedSongs(current_access_token)
print(f"{len(saved_songs)}")

# Get a list of all the songs currently in the Like-Mirror Playlist (results restricted to "fields")
# Example Result first value: {'uri': 'spotify:track:5A4Le7DS4KXVzC9gH5QRAh', 'name': 'God', 'added': '2023-10-11T19:52:53Z'}
print("- Getting Mirrored Songs... ", end="")
mirrored_songs = getAllPlaylistItems(current_access_token, LIKEMIRRORPLAYLISTID, "items(added_at,track(name,uri))")
print(f"{len(mirrored_songs)}")


print("- Tracks to add: ")
tracks_to_add = []

# Go through every saved song and search for it in the mirrored playlist. 
# If not present: add to the "to add" list 
for ss in saved_songs:
    present = False

    for ms in mirrored_songs:
        if ss["uri"] == ms["uri"]:
            present = True

    if not present:
        tracks_to_add.append(ss["uri"])
        print(f'  > {str(ss["name"]).ljust(50, " ")}   |   {ss["uri"]}')


# Add missing Tracks to Playlist
if len(tracks_to_add) == 0:
    print(f"  > Nothing ;)")

elif len(tracks_to_add) < 100:
    addTracksToPlaylist(current_access_token, LIKEMIRRORPLAYLISTID, tracks_to_add)
    print(f"- Tracks added successfully")

else:
    steps = 100
    tracks_to_add_split = []
    
    # Splitting the Lists into parts of 100
    for i in range(0, len(tracks_to_add), steps):  
        tracks_to_add_split.append(tracks_to_add[i:i+steps])

    # Adding Tracks to the Playlist in steps
    for track_part in tracks_to_add_split:
        addTracksToPlaylist(current_access_token, LIKEMIRRORPLAYLISTID, track_part)

    print(f"- Tracks added successfully")