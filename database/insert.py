import os
import uuid
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

# Connect to the Cassandra cluster
cluster = Cluster(['<Cassandra Docker IP>'])  # Replace with your Docker container IP
session = cluster.connect('media_keyspace')  # Connect to the 'media_keyspace'

# Prepare the insert statement for video data
insert_statement = SimpleStatement("""
    INSERT INTO videos (video_id, video_name, video_data, content_type, created_at)
    VALUES (%s, %s, %s, %s, %s)
""")

# Function to upload a video file to Cassandra
def upload_video(file_path):
    # Generate a unique video_id
    video_id = uuid.uuid4()

    # Get video file name and content type (MIME type)
    video_name = os.path.basename(file_path)
    content_type = 'video/mp4'  # Modify as needed (based on file type)

    # Read the video file as binary (BLOB)
    with open(file_path, 'rb') as file:
        video_data = file.read()

    # Get the current timestamp for video upload
    created_at = datetime.now()

    # Execute the insert statement with video data
    session.execute(insert_statement, (video_id, video_name, video_data, content_type, created_at))
    print(f"Video '{video_name}' uploaded successfully with ID: {video_id}")

# Upload the video located at '/var/www/media/test.mp4'
upload_video('/var/www/media/test.mp4')
