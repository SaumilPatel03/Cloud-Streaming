import os
import uuid
import datetime
import tempfile
from moviepy.video.io.VideoFileClip import VideoFileClip
from cassandra.cluster import Cluster

# Cassandra connection details
CASSANDRA_HOSTS = ['10.1.166.113', '10.1.58.64']  # Update with your node IPs
KEYSPACE = 'media1'  # Replace with your keyspace name

# Video chunking configuration
CHUNK_DURATION = 10  # Duration of each chunk in seconds
MEDIA_SERVER = 'local_server'  # Add a media server identifier

def connect_to_cassandra():
    """Establish connection to the Cassandra cluster."""
    cluster = Cluster(CASSANDRA_HOSTS)
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    return session

def split_video_into_chunks(video_path, chunk_duration):
    """Splits a video into smaller chunks and returns them as byte blobs."""
    video = VideoFileClip(video_path)
    total_duration = int(video.duration)  # Total duration of the video in seconds
    chunk_blobs = []

    print(f"Splitting video into {chunk_duration}-second chunks...")
    for start_time in range(0, total_duration, chunk_duration):
        end_time = min(start_time + chunk_duration, total_duration)
        # Extract chunk as bytes
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as temp_file:
            with video.subclipped(start_time, end_time) as chunk_video:
                # Remove audio to avoid potential subprocess issues
                chunk_video = chunk_video.without_audio()
                chunk_video.write_videofile(
                    temp_file.name, 
                    codec="libx264", 
                    audio=False  # Explicitly disable audio
                )
            with open(temp_file.name, "rb") as chunk_file:
                chunk_blob = chunk_file.read()
                chunk_blobs.append(chunk_blob)
    video.close()
    print(f"Video successfully split into {len(chunk_blobs)} chunks.")
    return chunk_blobs, total_duration, len(chunk_blobs)

def upload_video_metadata(session, video_id, title, description, duration, resolution, chunk_count):
    """Upload metadata for a video."""
    query = """
    INSERT INTO metadata (
        video_id, 
        title, 
        description, 
        upload_timestamp, 
        chunk_count, 
        resolution, 
        chunk_size, 
        media_servers
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(
        query,
        (
            video_id,
            title,
            description,
            datetime.datetime.utcnow(),
            chunk_count,
            resolution,
            CHUNK_DURATION,  # chunk_size
            [MEDIA_SERVER]   # media_servers
        ),
    )
    print(f"Uploaded metadata for video: {title}")

def upload_video_chunks(session, video_id, chunk_blobs):
    """Upload chunk information for a video, storing chunks as blobs."""
    query = """
    INSERT INTO video_chunks (
        video_id, 
        chunk_index, 
        chunk_data, 
        chunk_number, 
        media_server
    ) VALUES (%s, %s, %s, %s, %s)
    """
    for index, chunk_blob in enumerate(chunk_blobs, start=1):
        try:
            session.execute(query, (
                video_id,     # video_id
                index,        # chunk_index (1-based)
                chunk_blob,   # chunk_data
                index - 1,    # chunk_number (0-based)
                MEDIA_SERVER  # media_server
            ))
            print(f"Uploaded chunk {index} for video ID {video_id}")
        except Exception as e:
            print(f"Error uploading chunk {index}: {e}")
            import traceback
            traceback.print_exc()

def main():
    # Connect to Cassandra
    session = connect_to_cassandra()

    # Video details
    video_path = "/home/dhruv-hingu/Downloads/test.mp4"  # Local path to the video
    title = "test2.mp4"
    description = "This is a test file from Dhruv."
    resolution = "1080p"
    video_id = uuid.uuid4() 

    # Split the video into chunks
    chunk_blobs, duration, chunk_count = split_video_into_chunks(video_path, CHUNK_DURATION)

    # Upload video metadata
    upload_video_metadata(
        session, 
        video_id, 
        title, 
        description, 
        duration, 
        resolution, 
        chunk_count
    )

    # Upload video chunks
    upload_video_chunks(session, video_id, chunk_blobs)

    print("Video and chunk data uploaded successfully!")

if __name__ == "__main__":
    main()
