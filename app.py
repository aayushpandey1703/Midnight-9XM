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
        url=f"https://api.spotify.com/v1/search?q=tag:bollywood trending&type=album&market=IN&limit=20&offset=0"
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
            album={}
            album["id"]=i["id"]
            album["image"]=i["images"][-2]['url']
            album["title"]=i["name"]
            album["date"]=i["release_date"]
            artists=[a['name'] for a in i['artists']]
            album["author"]=",".join(artists)
            trending_albums.append(album)

        # Get Popular artists
        return render_template("index.htm",trending=trending_albums)
    except Exception as e:
        logger.error("Error in index:")
        logger.error(str(e))
        return render_template("error.htm")

if __name__=="__main__":
    app.run(debug=True,port="5000",host="0.0.0.0")