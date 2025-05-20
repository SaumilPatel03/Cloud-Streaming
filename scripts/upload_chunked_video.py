import os
import uuid
import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
from cassandra.cluster import Cluster

# Cassandra connection details
CASSANDRA_HOSTS = ['10.1.166.113', '10.1.58.64']  # Update with your node IPs
KEYSPACE = 'media'       # Replace with your keyspace name

# Video chunking configuration
CHUNK_DURATION = 10  # Duration of each chunk in seconds
CHUNK_OUTPUT_DIR = 'video_chunks'  # Directory to save the chunks

def connect_to_cassandra():
    """Establish connection to the Cassandra cluster."""
    cluster = Cluster(CASSANDRA_HOSTS)
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    return session

def split_video_into_chunks(video_path, output_dir, chunk_duration, video_id):
    """Splits a video into smaller chunks and saves them locally with unique names."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video = VideoFileClip(video_path)
    total_duration = int(video.duration)  # Total duration of the video in seconds
    chunk_paths = []

    print(f"Splitting video into {chunk_duration}-second chunks...")
    for start_time in range(0, total_duration, chunk_duration):
        end_time = min(start_time + chunk_duration, total_duration)
        # Include video_id and chunk_number to ensure uniqueness in naming
        chunk_filename = f"{video_id}_{start_time}-{end_time}.mp4"
        chunk_path = os.path.join(output_dir, chunk_filename)
        video.subclipped(start_time, end_time).write_videofile(chunk_path, codec="libx264")
        chunk_paths.append(chunk_path)

    video.close()
    print(f"Video successfully split into {len(chunk_paths)} chunks.")
    return chunk_paths


def upload_video_metadata(session, video_id, title, description, duration, file_path, resolution, bitrate):
    """Upload metadata for a video."""
    query = """
    INSERT INTO video_metadata (video_id, title, description, upload_date, duration, file_path, resolution, bitrate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (video_id, title, description, datetime.datetime.utcnow(), duration, file_path, resolution, bitrate))
    print(f"Uploaded metadata for video: {title}")

def upload_video_chunks(session, video_id, resolution, chunk_paths):
    """Upload chunk information for a video with unique chunk paths."""
    query = """
    INSERT INTO video_chunks (video_id, chunk_number, chunk_size, chunk_path, resolution)
    VALUES (%s, %s, %s, %s, %s)
    """
    for chunk_number, chunk_path in enumerate(chunk_paths, start=1):
        chunk_size = os.path.getsize(chunk_path)  # Get chunk size in bytes
        session.execute(query, (video_id, chunk_number, chunk_size, chunk_path, resolution))
        print(f"Uploaded chunk {chunk_number} for video ID {video_id}")

def main():
    # Connect to Cassandra
    session = connect_to_cassandra()

    # Video details
    video_path = "/home/dhruv-hingu/Downloads/test.mp4"  # Local path to the video
    title = "test.mp4"
    description = "This is a test file from dhruv."
    resolution = "1080p"
    bitrate = 4000  # Bitrate in kbps
    video_id = uuid.uuid4() 
    # Split the video into chunks
    chunk_paths = split_video_into_chunks(video_path, CHUNK_OUTPUT_DIR, CHUNK_DURATION,video_id)

    # Video metadata
    duration = int(VideoFileClip(video_path).duration)  # Duration in seconds
    file_path = video_path  # Store the path to the full video in metadata

    # Upload video metadata
    upload_video_metadata(session, video_id, title, description, duration, file_path, resolution, bitrate)

    # Upload video chunks
    upload_video_chunks(session, video_id, resolution, chunk_paths)

    print("Video and chunk data uploaded successfully!")

if __name__ == "__main__":
    main()
