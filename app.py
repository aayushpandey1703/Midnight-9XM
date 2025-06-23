from flask import Flask, render_template, redirect, url_for, make_response,request,session
import requests
from loguru import logger
import json
import functools
import psycopg2
import uuid

app=Flask(__name__)
app.secret_key="my_secret_key"

TOKEN=None
def token_generator(func):
    @functools.wraps(func)
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

def dbconnection():
    try:
        connection=psycopg2.connect(
            database="defaultdb",
            host="pg-336977da-aleronpeterson-6630.b.aivencloud.com",
            user="avnadmin",
            password="AVNS_TbvbOoIlAM6X64RKzxL",
            port=19275,
            sslmode="verify-ca",
            sslrootcert="./DB_cert/ca.pem"
        )
        return True,connection,None 
    except Exception as e:
        logger.error("Error connecting to DB")
        logger.error(str(e))
        return False, None,str(e)

@app.get("/")
@token_generator
def index():
    try:
        session_uid=request.cookies.get("session_uid",None)
        login_message=request.args.get("login_message",None)
        print(session_uid)
        if session_uid:
            userdata=session[session_uid]
        else:
            userdata=None
        # Get trending albums
        url=f"https://api.spotify.com/v1/search?q=tag:India trending&type=album&market=IN&limit=20&offset=0"
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

        return render_template("index.htm",userdata=userdata,trending=trending_albums,eng_trending=english_albums,artists_list=artists_list,workout_list=workout_list,login_message=login_message)
    except Exception as e:
        logger.error("Error in index function:")
        logger.error(str(e))
        return str(e)

@app.post("/register")
def register():
    try:
        print("POST")
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")
        print(username)
        print(email)
        print(password)
        status,connection,error=dbconnection()
        if connection:
            cursor=connection.cursor()
            query=f'''
            INSERT INTO "login" (username, email, password)
            VALUES ('{username}','{email}','{password}')
            RETURNING *;
                '''
            cursor.execute(query)
            userdata=cursor.fetchone()
            logger.info(userdata)
            connection.commit()
            cursor.close()
            connection.close()
            session_uid=str(uuid.uuid4())
            session[session_uid]={
                "userID": userdata[0],
                "username":userdata[1],
                "email":userdata[2]
            }
            response=make_response(redirect(url_for("index")))
            response.set_cookie("session_uid",session_uid,max_age=3600)
        else:
            raise Exception("Failed to connect to DB",str(error))
        
        return response
    except Exception as e:
        logger.error("Error in login")
        logger.error(str(e))
        return str(e)

@app.post("/login")
def login():
    try:
        email=request.form.get("email")
        password=request.form.get("password")
        print("email")
        print(email)
        print(password)
        status,connection,error=dbconnection()
        if connection:
            cursor=connection.cursor()
            cursor.execute(f"SELECT * FROM login where email='{email}' AND password='{password}';")
            user=cursor.fetchone()
            logger.info(user)
            if user is None:
                logger.error("[login GET] no user found")
                cursor.execute("SELECT * FROM login;")
                users=cursor.fetchall()
                logger.info(users)
                return redirect(url_for("index",login_message="User is not registered"))
            cursor.close()
            connection.close()
            session_uid=str(uuid.uuid4())
            session[session_uid]={
                "userID":user[0],
                "username":user[1],
                "email":user[2]
            }
            response=make_response(redirect(url_for("index")))
            response.set_cookie("session_uid",session_uid,max_age=3600)
        else:
            raise Exception("Failed to connect to DB",str(error))
        print
        return response
    except Exception as e:
        logger.error("Error in login")
        logger.error(str(e))
        return str(e)

@app.get("/webplayer")
@token_generator
def webplayer_get():
    try:
        print(TOKEN)
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
                f"https://api.spotify.com/v1/albums/{id}?market=IN",
                headers=header
            )
            if response.status_code!=200:
                raise Exception(f"request failed with status code:{response.status_code}")
            response_dict=response.json()
            track_cover["image"]=response_dict["images"][0]["url"]
            print(track_cover["image"])
            track_cover["name"]=response_dict["name"]
            track_cover["total_tracks"]=response_dict["total_tracks"]
            for i in response_dict["tracks"]["items"]:
                track={}
                # track_id=i["id"]
                # track_response=requests.get(
                #     f"https://api.spotify.com/v1/tracks/{track_id}",
                #     headers=header
                # )
                # track_dict=track_response.json()
                # if track_response.status_code==200:
                #     image_url=track_dict["album"]["images"][0]["url"]
                # else:
                #     image_url=None
                artists_list=[j["name"] for j in i["artists"]]
                track["artists"]=",".join(artists_list)
                track["name"]=i["name"]
                track["duration"]=i["duration_ms"]
                # track["image"]=image_url
                album_track.append(track)
            
        return render_template("webplayer.htm",album_cover=track_cover,album=album_track)
    except Exception as e:
        logger.error("Error in loading webplayer:")
        logger.error(str(e))
        return "Error in loading webplayer "+str(e)

@app.post("/playlist")
def playlist_add():
    try:
        trackID=request.form.get("trackID")
        playlistID=request.form.get("playlistID")
        logger.info(trackID)
        logger.info(playlistID)
        return "True"
    except Exception as e:
        logger.error("Error while adding to playlist")
        logger.error(str(e))
        return str(e)

@app.get("/logout")
def logout():
    try:
        session_uid=request.cookies.get("session_uid")
        response=make_response(redirect(url_for("index")))
        response.set_cookie("session_uid","",max_age=0)
        session.pop(session_uid)
        return response
    except Exception as e:
        logger.error("Error in logout")
        logger.error(str(e))
        return str(e)

if __name__=="__main__":
    app.run(debug=True,port="5000",host="0.0.0.0")