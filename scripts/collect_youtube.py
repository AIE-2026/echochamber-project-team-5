import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env
load_dotenv()

def get_channel_id(youtube, handle):
    """Translates a YouTube handle to a channel ID."""
    # Handles usually start with @, but we'll strip it just in case
    handle = handle if handle.startswith('@') else f"@{handle}"
    request = youtube.search().list(
        q=handle,
        type='channel',
        part='id',
        maxResults=1
    )
    response = request.execute()
    if not response.get('items'):
        raise ValueError(f"Could not find channel for handle: {handle}")
    return response['items'][0]['id']['channelId']

def get_recent_videos(youtube, channel_id, max_videos):
    """Gets the latest videos from a specific channel."""
    request = youtube.search().list(
        channelId=channel_id,
        part='snippet,id',
        order='date',
        type='video',
        maxResults=max_videos
    )
    response = request.execute()
    videos = []
    for item in response.get('items', []):
        videos.append({
            'video_id': item['id']['videoId'],
            'video_title': item['snippet']['title'],
            'video_date': item['snippet']['publishedAt']
        })
    return videos

def collect_comments(youtube, video, max_comments):
    """Collects comments for a specific video."""
    comments = []
    try:
        request = youtube.commentThreads().list(
            videoId=video['video_id'],
            part='snippet',
            maxResults=max_comments,
            textFormat='plainText'
        )
        response = request.execute()

        for item in response.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                "id": item['id'],
                "source_platform": "youtube",
                "source_channel": snippet['channelId'],
                "text_raw": snippet['textDisplay'],
                "video_id": video['video_id'],
                "video_title": video['video_title'],
                "video_date": video['video_date'],
                "comment_date": snippet['publishedAt'],
                "likes": snippet['likeCount'],
                "collected_at": datetime.utcnow().isoformat() + "Z"
            })
    except Exception as e:
        print(f"Could not collect comments for {video['video_id']}: {e}")
    
    return comments

def main():
    parser = argparse.ArgumentParser(description="Collect YouTube comments from a handle.")
    parser.add_argument("--handle", required=True, help="YouTube handle (e.g., digi24hd56)")
    parser.add_argument("--max-videos", type=int, default=2, help="Max videos to scan")
    parser.add_argument("--max-comments", type=int, default=50, help="Max comments per video")
    parser.add_argument("--output", required=True, help="Path to output JSONL file")

    args = parser.parse_args()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env file.")
        return

    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        print(f"Resolving handle {args.handle}...")
        channel_id = get_channel_id(youtube, args.handle)
        
        print(f"Fetching latest {args.max_videos} videos...")
        videos = get_recent_videos(youtube, channel_id, args.max_videos)
        
        all_comments = []
        for v in videos:
            print(f"Collecting comments for video: {v['video_title']}...")
            all_comments.extend(collect_comments(youtube, v, args.max_comments))

        # Ensure output directory exists
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

        print(f"Saving {len(all_comments)} comments to {args.output}...")
        with open(args.output, 'w', encoding='utf-8') as f:
            for comment in all_comments:
                f.write(json.dumps(comment, ensure_ascii=False) + '\n')
        
        print("Done!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()