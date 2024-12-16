import os
import uuid
import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
from cassandra.cluster import Cluster

# Cassandra connection details
CASSANDRA_HOSTS = ['10.1.166.113', '10.1.58.64']  # Update with your node IPs
KEYSPACE = 'media1'  # Replace with your keyspace name

# Video chunking configuration
CHUNK_DURATION = 10  # Duration of each chunk in seconds


def connect_to_cassandra():
    """Establish connection to the Cassandra cluster."""
    cluster = Cluster(CASSANDRA_HOSTS)
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    return session


def split_video_into_chunks(video_path, chunk_duration, video_id):
    """Splits a video into smaller chunks and returns them as byte blobs."""
    video = VideoFileClip(video_path)
    total_duration = int(video.duration)  # Total duration of the video in seconds
    chunk_blobs = []

    print(f"Splitting video into {chunk_duration}-second chunks...")
    for start_time in range(0, total_duration, chunk_duration):
        end_time = min(start_time + chunk_duration, total_duration)
        # Extract chunk as bytes
        chunk_filename = f"{video_id}_{start_time}-{end_time}.mp4"
        with video.subclipped(start_time, end_time) as chunk_video:
            chunk_path = f"/tmp/{chunk_filename}"
            chunk_video.write_videofile(chunk_path, codec="libx264")
            with open(chunk_path, "rb") as chunk_file:
                chunk_blob = chunk_file.read()
                chunk_blobs.append(chunk_blob)
            os.remove(chunk_path)  # Clean up temporary file
    video.close()
    print(f"Video successfully split into {len(chunk_blobs)} chunks.")
    return chunk_blobs


def upload_video_metadata(session, video_id, title, description, duration, resolution, bitrate, chunk_count):
    """Upload metadata for a video."""
    query = """
    INSERT INTO metadata (video_id, title, description, upload_timestamp, chunk_count, resolution)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    session.execute(
        query,
        (
            video_id,
            title,
            description,
            datetime.datetime.utcnow(),
            chunk_count,
            resolution
            
        ),
    )
    print(f"Uploaded metadata for video: {title}")


def upload_video_chunks(session, video_id, resolution, chunk_blobs):
    """Upload chunk information for a video, storing chunks as blobs."""
    query = """
    INSERT INTO video_chunks (video_id, chunk_index, chunk_data)
    VALUES (%s, %s, %s)
    """
    for chunk_index, chunk_blob in enumerate(chunk_blobs, start=1):
        session.execute(query, (video_id, chunk_index, chunk_blob))
        print(f"Uploaded chunk {chunk_index} for video ID {video_id}")


def main():
    # Connect to Cassandra
    session = connect_to_cassandra()

    # Video details
    video_path = "/home/saumil/Downloads/Cloud/bio.mp4"  # Local path to the video
    title = "bio.mp4"
    description = "This is a test file from Saumil2."
    resolution = "1080p"
    bitrate = 4000  # Bitrate in kbps
    video_id = uuid.uuid4() 

    # Split the video into chunks
    chunk_blobs = split_video_into_chunks(video_path, CHUNK_DURATION, video_id)
    chunk_count = len(chunk_blobs)

    # Video metadata
    duration = int(VideoFileClip(video_path).duration)  # Duration in seconds

    # Upload video metadata
    upload_video_metadata(session, video_id, title, description, duration, resolution, bitrate, chunk_count)

    # Upload video chunks
    upload_video_chunks(session, video_id, resolution, chunk_blobs)

    print("Video and chunk data uploaded successfully!")


if __name__ == "__main__":
    main()
