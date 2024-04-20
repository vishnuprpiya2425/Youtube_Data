import mysql.connector
import os
import googleapiclient.discovery
import googleapiclient.errors
import json
import pandas as pd
import streamlit as st
import requests_cache
from googleapiclient.discovery import build


# import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()

# API Key Connection 

def Api_connect():
    Api_Id= "AIzaSyC9ZTBxS71e03AB1AJeMMSn3WKU3mAgN-w"

    api_service_name="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    return youtube

youtube=Api_connect()

# Get channel info 
# Define a function to get channel info
def get_channel_info(channel_id):
    # Initialize YouTube API client
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyC9ZTBxS71e03AB1AJeMMSn3WKU3mAgN-w"  # Replace with your actual API key
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Make request to get channel info
    request = youtube.channels().list(
        part="snippet, contentDetails, statistics",
        id=channel_id
    )
    response = request.execute()
    for i in response['items']:
        data=dict(channel_Name=i["snippet"]["title"],
                channel_Id=i["id"],
                subscribe=i["statistics"]["subscriberCount"],
                views=i['statistics']['viewCount'],
                Total_videos=i["statistics"]["videoCount"],
                channel_descrpition=i["snippet"]["description"],
                Playlist_id=i["contentDetails"]["relatedPlaylists"]["uploads"])

    return data

import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS channel_info (
                        channel_Name VARCHAR(255),
                        channel_Id VARCHAR(255),
                        subscribe INT,
                        views INT,
                        Total_videos INT,
                        Channel_Description TEXT,
                        Playlist_id VARCHAR(255)
                    )""")

mydb.close()

#Get Video Ids
def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,
                                     part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token=None

    while True:
        response1=youtube.playlistItems().list(
            part='snippet',
            playlistId=Playlist_Id,
            maxResults=50,
            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids

import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS video_ids (
                        video_id VARCHAR(255)
                    )""")

mydb.close

# Get Video information

def get_video_info(video_Ids):
    video_data=[]
    for video_id in video_Ids:
        request=youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response=request.execute()

        for item in response["items"]:
            data=dict(channel_Name=item['snippet']['channelTitle'],
                      channel_Id=item['snippet']['channelId'],
                      video_Id=item['id'],
                      Title=item['snippet']['title'],
                      Tags=item.get('tags'),
                      Thumbnail=item['snippet']['thumbnails'],
                      Description=item.get('description'),
                      Published_date=item['snippet']['publishedAt'],
                      Duration=item['contentDetails']['duration'],
                      view=item.get('viewCount'),
                      likes=item['statistics'].get('likeCount'),
                      dislikes=item['statistics'].get('dislikeCount'),
                      comments=item['statistics'].get('commentCount')
                      )
            video_data.append(data)
    return video_data

import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS videos (
                channel_Name VARCHAR(255),
                channel_Id VARCHAR(255),
                video_Id VARCHAR(255),
                Title VARCHAR(255),
                Tags TEXT,
                Thumbnail TEXT,
                Description TEXT,
                Published_date VARCHAR(255),
                Duration VARCHAR(255),
                view INT,
                likes INT,
                dislikes INT,
                comments INT
            )""")

mydb.close()

# Get Comment Information 

def get_comment_info(video_ids):
    comment_data=[]
    try:
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(comment_Id=item['snippet']['topLevelComment']['id'],
                          video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                          comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                          comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                          comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                
                comment_data.append(data)

    except:
        pass
    return comment_data            



import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS comment_info (
                            comment_Id VARCHAR(255),
                            video_Id VARCHAR(255),
                            comment_Text TEXT,
                            comment_Author VARCHAR(255),
                            comment_Published VARCHAR(255)
                        )""")

mydb.close()

# Get playlist Details 
def get_playlist_details(channel_id):
    All_data=[]
    request=youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=50
    )
    response=request.execute()

    for item in response['items']:
        Playlist_Id=item['id']
        Title=item['snippet']['title']
        Published_date=item['snippet']['publishedAt'].replace('T', ' ').replace('Z', '')
        video_count=item['contentDetails']['itemCount']

        # Fetch video IDs in the playlist
        video_ids = []
        next_page_token = None
        while True:
            playlist_items_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=Playlist_Id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_items_response = playlist_items_request.execute()

            for playlist_item in playlist_items_response["items"]:
                video_ids.append(playlist_item["snippet"]["resourceId"]["videoId"])

            next_page_token = playlist_items_response.get("nextPageToken")
            if not next_page_token:
                break

        for video_id in video_ids:
            data=dict(Playlist_Id=Playlist_Id,
                        channel_Name=item['snippet']['channelTitle'],
                        channel_Id=channel_id,
                        video_Id=video_id,
                        Title=Title,
                        Published_date=Published_date,
                        video_count=video_count)
            All_data.append(data)



    return All_data

import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS playlist_details (
                            Playlist_Id VARCHAR(255),
                            channel_Name VARCHAR(255),
                            channel_Id VARCHAR(255),
                            video_Id VARCHAR(255),
                            Title VARCHAR(255),
                            Published_date VARCHAR(255),
                            video_count INT
                        )""")

mydb.close()


def get_channel_details(channel_id):
    channel_details = get_channel_info(channel_id)
    Video_Ids = get_videos_ids(channel_id)
    video_details = get_video_info(Video_Ids)
    comment_details = get_comment_info(Video_Ids)
    playlist_details = get_playlist_details(channel_id)

    # Convert dictionaries to DataFrames
    channel_df = pd.DataFrame([channel_details])
    video_df = pd.DataFrame(video_details)
    comment_df = pd.DataFrame(comment_details)
    playlist_df = pd.DataFrame(playlist_details)
    
    return {
        "channel_details": channel_df,
        "video_details": video_df,
        "comment_details": comment_df,
        "playlist_details": playlist_df,
    }


# Function to insert data into the channel_info table
# import mysql.connector


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='youtube_data'
)

cursor = mydb.cursor()

# Define a function to get channel info
def get_channel_info(channel_id):
    # Initialize YouTube API client
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyC9ZTBxS71e03AB1AJeMMSn3WKU3mAgN-w"  # Replace with your actual API key
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Make request to get channel info
    request = youtube.channels().list(
        part="snippet, contentDetails, statistics",
        id=channel_id
    )
    response = request.execute()

    data = {}
    for item in response['items']:
        data['channel_Name'] = item["snippet"]["title"]
        data['channel_Id'] = item["id"]
        data['subscribe'] = item["statistics"]["subscriberCount"]
        data['views'] = item['statistics']['viewCount']
        data['Total_videos'] = item["statistics"]["videoCount"]
        data['channel_description'] = item["snippet"]["description"]
        data['Playlist_id'] = item["contentDetails"]["relatedPlaylists"]["uploads"]

    return data

def insert_channel_info(data):
    try:
        channel_Id = data['channel_Id']
        cursor.execute("SELECT * FROM channel_info WHERE channel_Id = %s", (channel_Id,))
        result = cursor.fetchone()

        if not result:
            sql = "INSERT INTO channel_info (channel_Name, channel_Id, subscribe, views, Total_videos, channel_description, Playlist_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (data['channel_Name'], data['channel_Id'], data['subscribe'], data['views'], data['Total_videos'], data['channel_description'], data['Playlist_id'])
            cursor.execute(sql, val)
            mydb.commit()
            print("Data inserted successfully!")
        else:
            print("Record already exists in the table")
    except mysql.connector.Error as error:
        print("Failed to insert record into channel_info table {}".format(error))

# Function to insert data into the video_ids table
import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()

def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id, part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token=None

    while True:
        response1=youtube.playlistItems().list(
            part='snippet',
            playlistId=Playlist_Id,
            maxResults=50,
            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids
# Function to insert video IDs into the database
def insert_video_ids(video_ids):
    try:
        for video_id in video_ids:
            cursor.execute("SELECT * FROM video_ids WHERE video_id = %s", (video_id,))
            result = cursor.fetchone()

            if not result:
                sql = "INSERT INTO video_ids (video_id) VALUES (%s)"
                val = (video_id,)
                cursor.execute(sql, val)
        mydb.commit()
        print("Video IDs inserted successfully!")
    except Exception as e:
        print("Failed to insert video IDs:", e)


# Function to insert data into the videos table
import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()

# Function to get video information
def get_video_info(video_Ids):
    video_data = []
    for video_id in video_Ids:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()

        for item in response["items"]:
            data = {
                'channel_Name': item['snippet']['channelTitle'],
                'channel_Id': item['snippet']['channelId'],
                'video_Id': item['id'],
                'Title': item['snippet']['title'],
                'Tags': item.get('tags'),
                'Thumbnail': item['snippet']['thumbnails'],
                'Description': item.get('description'),
                'Published_date': item['snippet']['publishedAt'],
                'Duration': item['contentDetails']['duration'],
                'view': item['statistics'].get('viewCount'),
                'likes': item['statistics'].get('likeCount'),
                'dislikes': item['statistics'].get('dislikeCount'),
                'comments': item['statistics'].get('commentCount')
            }
            video_data.append(data)
    return video_data

def insert_videos(video_data):
    for data in video_data:
        video_Id = data['video_Id']
        cursor.execute("SELECT * FROM videos WHERE video_Id = %s", (video_Id,))
        result = cursor.fetchone()

        if not result:
            # Convert Thumbnail dictionary to a string
            thumbnail_str = json.dumps(data['Thumbnail'])
            sql = "INSERT INTO videos (channel_Name, channel_Id, video_Id, Title, Tags, Thumbnail, Description, Published_date, Duration, view, likes, dislikes, comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (data['channel_Name'], data['channel_Id'], data['video_Id'], data['Title'], data['Tags'], thumbnail_str, data['Description'], data['Published_date'], data['Duration'], data['view'], data['likes'], data['dislikes'], data['comments'])
            cursor.execute(sql, val)
    mydb.commit()


# Function to insert data into the comment_info table
import mysql.connector
mydb=mysql.connector.connect(
 host='localhost',
 user='root',
 password='root',
 database='youtube_data')

cursor = mydb.cursor()

def get_comment_info(video_Ids):
    comment_data=[]
    try:
        for video_id in video_Ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(comment_Id=item['snippet']['topLevelComment']['id'],
                          video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                          comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                          comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                          comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                
                comment_data.append(data)

    except:
        pass
    return comment_data          
def insert_comment_info(comment_data):
    for data in comment_data:
        comment_Id = data['comment_Id']
        cursor.execute("SELECT * FROM comment_info WHERE comment_Id = %s", (comment_Id,))
        result = cursor.fetchone()

        if not result:
            sql = "INSERT INTO comment_info (comment_Id, video_Id, comment_Text, comment_Author, comment_Published) VALUES (%s, %s, %s, %s, %s)"
            val = (data['comment_Id'], data['video_Id'], data['comment_Text'], data['comment_Author'], data['comment_Published'])
            cursor.execute(sql, val)
    mydb.commit()

# Function to insert data into the playlist_details table
# import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='youtube_data')

cursor = mydb.cursor()

def get_playlist_details(channel_id):
    next_page_token = None
    All_data = []
    while True:
        request = youtube.playlists().list(
            part='snippet,contentDetails',
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            data = {
                'Playlist_Id': item['id'],  # Corrected key name
                'channel_Name': item['snippet']['channelTitle'],
                'channel_Id': item['snippet']['channelId'],
                'video_Id': item['id'],
                'Title': item['snippet']['title'],
                'Published_date': item['snippet']['publishedAt'].replace('T', ' ').replace('Z', ''),
                'video_count': item['contentDetails']['itemCount']
            }
            All_data.append(data)

        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break
    return All_data

def insert_playlist_details(playlist_details):
    for data in playlist_details:
        Playlist_Id = data['Playlist_Id']
        cursor.execute("SELECT * FROM playlist_details WHERE Playlist_Id = %s", (Playlist_Id,))
        result = cursor.fetchone()

        if not result:
            sql = "INSERT INTO playlist_details (Playlist_Id, channel_Name, channel_Id, video_Id, Title, Published_date, video_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (data['Playlist_Id'], data['channel_Name'], data['channel_Id'], data['video_Id'], data['Title'], data['Published_date'], data['video_count'])
            cursor.execute(sql, val)
    mydb.commit()



# Streamlit app
import streamlit as st

def main():
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select an option", ["Home", "Channel Details", "Go to Question"])

    if option == "Home":
        st.title(":red[YOUTUBE DATA HAVERSTING AND WAREHOUSING]")
    elif option == "Channel Details":
        st.title('YouTube Channel Details')
        channel_id = st.text_input('Enter YouTube Channel ID:', key='channel_id_input')
        if st.button('Get Channel Details'):
            details = get_channel_details(channel_id)
            st.subheader('Channel Details')
            st.write(details["channel_details"])

            st.subheader('Video Details')
            st.write(details["video_details"])

            st.subheader('Comment Details')
            st.write(details["comment_details"])

            st.subheader('Playlist Details')
            st.write(details["playlist_details"])

            st.session_state.details = details  # Store details in session state

        if st.button('Insert Data'):
            try:
                insert_channel_info(st.session_state.details["channel_details"].iloc[0].to_dict())
                insert_video_ids(st.session_state.details["video_details"]["video_Id"].tolist())
                insert_videos(st.session_state.details["video_details"].to_dict('records'))
                insert_comment_info(st.session_state.details["comment_details"].to_dict('records'))
                insert_playlist_details(st.session_state.details["playlist_details"].to_dict('records'))
            except Exception as e:
                st.error(f"Error inserting data: {e}")

    elif option == "Go to Question":
        st.session_state.page = 'questions_page'


def questions_page():
    questions = [
        "Names of all the videos and their corresponding channels",
        "Channels with the most number of videos and how many videos they have",
        "Top 10 most viewed videos and their respective channels",
        "Number of comments for each video and their corresponding video names",
        "Videos with the highest number of likes and their corresponding channel names",
        "Total number of likes and dislikes for each video and their corresponding video names",
        "Total number of views for each channel and their corresponding channel names",
        "Names of all the channels that have published videos in the year 2022",
        "Average duration of all videos in each channel and their corresponding channel names",
        "Videos with the highest number of comments and their corresponding channel names"
    ]

    selected_question = st.selectbox("Select a question", questions, key="selectbox_unique_key")

    # Fetch data based on the selected question
    if st.button('Submit'):
        if selected_question == questions[0]:
            cursor.execute("SELECT  Title, channel_name FROM videos")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['video Title','Channel_Name'])
            st.write(df)

        
           
        elif selected_question == questions[1]:
            cursor.execute("SELECT channel_name, COUNT(*) as video_count FROM videos GROUP BY channel_name ORDER BY video_count DESC")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Channel_Name', 'No of videos'])
            st.write(df)

        

        elif selected_question == questions[2]:
            cursor.execute("SELECT Title, channel_name, view FROM videos ORDER BY view DESC LIMIT 10")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Video_Title', 'Channel name','View Count'])
            st.write(df)

          
        elif selected_question == questions[3]:
            cursor.execute("SELECT Title, COUNT(*) as comments FROM videos GROUP BY Title")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Video Title', 'No of comments'])
            st.write(df)


        elif selected_question == questions[4]:
            cursor.execute("SELECT MAX(likes) as max_likes FROM videos")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Highest Likes'])
            st.write(df)

           

        elif selected_question == questions[5]:
            cursor.execute("SELECT Title, SUM(likes) as total_likes, SUM(dislikes) as total_dislikes FROM videos GROUP BY Title")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Video Title','Like Count','Dislike Count'])
            st.write(df)

        elif selected_question == questions[6]:
            cursor.execute("SELECT channel_name, SUM(view) as total_views FROM videos GROUP BY channel_name")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Channel Name', 'No of views'])
            st.write(df)

            

        elif selected_question == questions[7]:
            cursor.execute("SELECT DISTINCT channel_name FROM videos WHERE YEAR(published_date) = 2022")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Channel Name'])
            st.write(df)

            
            

        elif selected_question == questions[8]:
            cursor.execute("""SELECT channel_name, AVG(duration_minutes) AS avg_duration 
                        FROM (
                                SELECT channel_name, TIME_TO_SEC(SUBSTRING(duration, 3)) / 60 AS duration_minutes 
                                FROM videos
                            ) AS durations 
                            GROUP BY channel_name """)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Channel Name', 'Average Sec'])
            st.write(df)
            
           

        
        elif selected_question == questions[9]:
            cursor.execute("""SELECT Title, channel_name, COUNT(*) as comment_count 
                FROM videos 
                GROUP BY Title, channel_name 
                ORDER BY comment_count DESC 
                LIMIT 1
            """)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Channel Title', 'Channel Name','No of Counts'])
            st.write(df)

           
    
    if st.button('Go to Home Page'):
        st.session_state.page = 'main_page'


if __name__ == '__main__':
    if 'page' not in st.session_state:
        st.session_state.page = 'main_page'

    if st.session_state.page == 'main_page':
        main()
    elif st.session_state.page == 'questions_page':
        questions_page()

    mydb.close()