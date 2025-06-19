from flask import Flask, render_template, redirect, url_for, make_response,request
import requests
from loguru import logger
import json

app=Flask(__name__)

TOKEN=None
def token_generator(func):
    def wrapper(*args, **kwargs):
        global TOKEN
        logger.debug("Generating token...")
        data={
            "grant_type": "client_credentials"
            # "client_id":"ae66df0606854547bc485a5ae566d942",
            # "client_secret":"2aae1a247a584914b862eeb37bb64fe8"
        }
        header={
            "Authorization":"Basic YWU2NmRmMDYwNjg1NDU0N2JjNDg1YTVhZTU2NmQ5NDI6MmFhZTFhMjQ3YTU4NDkxNGI4NjJlZWIzN2JiNjRmZTg=",
            "Content-Type":"application/x-www-form-urlencoded"
        }
        response=requests.post(
            "https://accounts.spotify.com/api/token",
            headers=header,
            data=data
        )
        response_json=response.json()
        TOKEN=response_json["access_token"]
        print(TOKEN)
        return func(*args, **kwargs)
    return wrapper

@app.get("/")
@token_generator
def index():
    try:
        # Get trending albums
        url=f"https://api.spotify.com/v1/search?q=tag:India best&type=album&market=IN&limit=20&offset=0"
        header={
            "Authorization":f"Bearer {TOKEN}"
        }
        response=requests.get(
            url,
            headers=header
        )
        if response.status_code!=200:
            raise Exception("response code"+str(response.status_code+"\nError message: "+str(response.json())))
        items=response.json()["albums"]["items"]
        trending_albums=[]
        for i in items:
            if i["album_type"] != "single":
                album={}
                album["id"]=i["id"]
                album["image"]=i["images"][-2]['url']
                album["title"]=i["name"]
                album["date"]=i["release_date"]
                artists=[a['name'] for a in i['artists']]
                album["author"]=",".join(artists)
                album["tracks"]=i["total_tracks"]
                trending_albums.append(album)

        # Get English Trending album
        url=f"https://api.spotify.com/v1/search?q=tag:popular english&type=album&market=IN&limit=20&offset=0"
        header={
            "Authorization":f"Bearer {TOKEN}"
        }
        response=requests.get(
            url,
            headers=header
        )
        if response.status_code!=200:
            raise Exception("response code"+str(response.status_code+"\nError message: "+str(response.json())))
        items=response.json()["albums"]["items"]
        english_albums=[]
        for i in items:
            album={}
            album["id"]=i["id"]
            album["image"]=i["images"][-2]['url']
            album["title"]=i["name"]
            album["date"]=i["release_date"]
            artists=[a['name'] for a in i['artists']]
            album["author"]=",".join(artists)
            album["tracks"]=i["total_tracks"]
            english_albums.append(album)

        # Get popular artists
        url=f"https://api.spotify.com/v1/search?q=tag:trending english&type=artist&market=IN&limit=20&offset=0"
        header={
            "Authorization":f"Bearer {TOKEN}"
        }
        response=requests.get(
            url,
            headers=header
        )
        if response.status_code!=200:
            raise Exception("response code"+str(response.status_code+"\nError message: "+str(response.json())))
        items=response.json()["artists"]["items"]
        artists_list=[]
        for i in items:
            if i is not None:
                album={}
                album["id"]=i["id"]
                album["followers"]=i["followers"]["total"]
                if len(i['images'])>=2:
                    album["image"]=i["images"][-2]['url']
                else:
                    album['image']="https://cdn.britannica.com/62/236062-050-CD53AE96/Ampersand-symbol.jpg"
                album["title"]=i["name"]
                artists_list.append(album)

        # Get workout playlist
        url=f"https://api.spotify.com/v1/search?q=tag:Workout&type=playlist&market=IN&limit=20&offset=0"
        header={
            "Authorization":f"Bearer {TOKEN}"
        }
        response=requests.get(
            url,
            headers=header
        )
        if response.status_code!=200:
            raise Exception("response code"+str(response.status_code+"\nError message: "+str(response.json())))
        items=response.json()["playlists"]["items"]
        workout_list=[]
        for i in items:
            if i is not None:
                album={}
                album["id"]=i["id"]
                # album["followers"]=i["followers"]["total"]
                if len(i['images'])>=2:
                    album["image"]=i["images"][-2]['url']
                else:
                    album['image']="https://static.vecteezy.com/system/resources/thumbnails/013/250/427/small_2x/music-notation-illustration-for-icon-symbol-art-illustration-apps-website-logo-or-graphic-design-element-format-png.png"
                album["title"]=i["name"]
                album["author"]=i["owner"]["display_name"]
                album["tracks"]=i["tracks"]["total"]
                workout_list.append(album)

        return render_template("index.htm",trending=trending_albums,eng_trending=english_albums,artists_list=artists_list,workout_list=workout_list)
    except Exception as e:
        logger.error("Error in index function:")
        logger.error(str(e))
        return render_template("error.htm")

@app.get("/webplayer")
# @token_generator
def webplayer_get():
    try:
        header={
            "Authorization":f"Bearer {TOKEN}"
        }
        id=request.args.get("id")
        type=request.args.get("type")
        if type=="album":
            track_cover={}
            album_track=[]
            track={}
            response=requests.get(
                f"https://api.spotify.com/v1/albums?id={id}&market=IN",
                headers=header
            )
            response_dict=response.json()
            track_cover["image"]=response_dict["images"][0]
            track_cover["name"]=response_dict["name"]
            track_cover["total_tracks"]=response_dict["total_tracks"]
            for i in response_dict["tracks"]["items"]:
                artists_list=[j["name"] for j in i["artists"]]
                track["artists"]=",".join(artists_list)
                track["name"]=i["name"]
                track["duration"]=i["durattion_ms"]
                album_track.append(track)
                        
        return render_template("webplayer.htm",album_cover=track_cover,album_track=album_track)
    except Exception as e:
        logger.error("Error in loading webplayer:")
        logger.error(str(e))
        return "Error in loading webplayer "+str(e)

if __name__=="__main__":
    app.run(debug=True,port="5000",host="0.0.0.0")