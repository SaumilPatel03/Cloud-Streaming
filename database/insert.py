import os
import uuid
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import ffmpeg  # Install with `pip install imageio[ffmpeg]`

# Connect to Cassandra
cluster = Cluster(['172.17.0.1'])  # Replace with Cassandra Docker IP
session = cluster.connect('media_keyspace')

# Insert statement for video chunks
insert_statement = SimpleStatement("""
    INSERT INTO video_chunks (video_id, chunk_index, video_name, chunk_data, content_type, created_at, duration, bitrate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""")

def get_video_metadata(file_path):
    """Retrieve duration and bitrate of the video using ffmpeg."""
    probe = ffmpeg.probe(file_path)
    format_info = probe['format']
    duration = float(format_info['duration'])  # Duration in seconds
    bitrate = int(format_info['bit_rate'])  # Bitrate in bits per second
    return duration, bitrate

def upload_video(file_path):
    video_id = uuid.uuid4()
    video_name = os.path.basename(file_path)
    content_type = 'video/mp4'
    created_at = datetime.now()
    chunk_size = 8 * 1024 * 1024  # 8 MB chunks

    # Get video metadata
    duration, bitrate = get_video_metadata(file_path)
    duration = int(duration)  # Convert duration to an integer
    bitrate = int(bitrate)  # Ensure bitrate is an integer

    with open(file_path, 'rb') as file:
        chunk_index = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            session.execute(insert_statement, (video_id, chunk_index, video_name, chunk, content_type, created_at, duration, bitrate))
            chunk_index += 1
    print(f"Video '{video_name}' uploaded successfully with ID: {video_id}")


# Upload the video
upload_video('/var/www/media/bigb.mp4')
