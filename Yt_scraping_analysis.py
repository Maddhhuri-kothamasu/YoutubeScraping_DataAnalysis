# Importing required libraries
from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns

# YouTube API key (generate your own API key from the YouTube Developer Console)
youtube_api_key = 'YOUR_YOUTUBE_API_KEY'

# List of YouTube channel IDs to fetch statistics for
channel_ids = ['CHANNEL_ID_1', 'CHANNEL_ID_2', 'CHANNEL_ID_3', ...]

# Build the YouTube API client
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

# Function to get channel statistics for the given list of channel IDs
def get_channel_stats(youtube, channel_ids):
    all_channel_data = []
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    response = request.execute() 
    
    # Loop through the response to extract required data
    for i in range(len(response['items'])):
        channel_data = dict(
            Channel_name=response['items'][i]['snippet']['title'],
            Subscribers=response['items'][i]['statistics']['subscriberCount'],
            Views=response['items'][i]['statistics']['viewCount'],
            Total_videos=response['items'][i]['statistics']['videoCount'],
            playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
        )
        all_channel_data.append(channel_data)
    
    return all_channel_data

# Fetch channel statistics for the provided channel IDs
channel_statistics = get_channel_stats(youtube, channel_ids)

# Convert the data into a pandas DataFrame
channel_data = pd.DataFrame(channel_statistics)

# Convert Subscribers, Views, and Total_videos to numeric data types
channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])

# Set the figure size for seaborn plots
sns.set(rc={'figure.figsize':(10,8)})

# Plot the number of subscribers for each channel
ax_subscribers = sns.barplot(x='Channel_name', y='Subscribers', data=channel_data)

# Plot the number of views for each channel
ax_views = sns.barplot(x='Channel_name', y='Views', data=channel_data)

# Plot the total number of videos for each channel
ax_total_videos = sns.barplot(x='Channel_name', y='Total_videos', data=channel_data)

# Fetch the playlist ID for a specific channel (e.g., 'Ken Jee')
ken_jee_playlist_id = channel_data.loc[channel_data['Channel_name'] == 'Ken Jee', 'playlist_id'].iloc[0]

# Function to get video IDs from a playlist
def get_video_ids(youtube, playlist_id):
    video_ids = []
    next_page_token = None
    more_pages = True

    while more_pages:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            more_pages = False

    return video_ids

# Fetch video IDs from the specified playlist
video_ids = get_video_ids(youtube, ken_jee_playlist_id)

# Function to get video details based on video IDs
def get_video_details(youtube, video_ids):
    all_video_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response['items']:
            video_stats = dict(
                Title=video['snippet']['title'],
                Published_date=video['snippet']['publishedAt'],
                Views=video['statistics']['viewCount'],
                Likes=video['statistics']['likeCount'],
                Dislikes=video['statistics']['dislikeCount'],
                Comments=video['statistics']['commentCount']
            )
            all_video_stats.append(video_stats)

    return all_video_stats

# Fetch video details for the provided video IDs
video_details = get_video_details(youtube, video_ids)

# Convert the video details into a pandas DataFrame
video_data = pd.DataFrame(video_details)

# Convert Published_date, Views, Likes, and Dislikes to appropriate data types
video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Dislikes'] = pd.to_numeric(video_data['Dislikes'])

# Get the top 10 videos with the most views
top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)

# Plot the top 10 videos with the most views
ax_top10_views = sns.barplot(x='Views', y='Title', data=top10_videos)

# Extract the month from the Published_date and create a new 'Month' column
video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')

# Group videos by month and count the number of videos in each month
videos_per_month = video_data.groupby('Month', as_index=False).size()

# Define the sort order for the months
sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Sort the videos_per_month DataFrame based on the sort_order
videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories=sort_order, ordered=True)
videos_per_month = videos_per_month.sort_index()

# Plot the number of videos uploaded per month
ax_videos_per_month = sns.barplot(x='Month', y='size', data=videos_per_month)

# Save the video details DataFrame to a CSV file
video_data.to_csv('Video_Details(Ken Jee).csv')

    