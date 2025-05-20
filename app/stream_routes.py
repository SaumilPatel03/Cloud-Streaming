from flask import Flask, Response
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import os
import uuid
app = Flask(__name__)

# Connect to Cassandra
def get_cassandra_session():
    cluster = Cluster(['10.1.58.64'])  # Replace with your Cassandra IPs
    session = cluster.connect('media')  # Connect to the keyspace
    return session

# Fetch video chunk paths from Cassandra
def fetch_video_chunks(video_id):
    session = get_cassandra_session()
    query = SimpleStatement("""
        SELECT chunk_number, chunk_path FROM video_chunks 
        WHERE video_id = %s
        ALLOW FILTERING
    """)
    rows = session.execute(query, (uuid.UUID(video_id),))
    return rows

# Fetch chunk data (from local storage or a network share)
def fetch_chunk_data(chunk_path):
    try:
        # Open the chunk file from the local file system or network location
        with open(chunk_path, 'rb') as chunk_file:
            data = chunk_file.read()
            print(f"Fetched chunk: {chunk_path}, size: {len(data)} bytes")
            return data  # Read the file as bytes
    except Exception as e:
        print(f"Error reading chunk {chunk_path}: {e}")
        return None

# Generator function to stream video chunks one by one
def generate_video(video_chunks):
    for chunk in video_chunks:
        chunk_data = fetch_chunk_data(chunk.chunk_path)
        if chunk_data:
            yield chunk_data  # Yield chunk data for streaming
        else:
            yield b''  # In case of error, send empty data

# Stream video route
@app.route('/video/<video_id>')
def stream_video(video_id):
    # Fetch video chunk paths from Cassandra
    video_chunks = fetch_video_chunks(video_id)
    
    if not video_chunks:
        return "Video not found", 404

    # Ensure chunks are ordered by chunk_number
    video_chunks = sorted(video_chunks, key=lambda x: x.chunk_number)

    # Generate the response using the generator
    return Response(
        generate_video(video_chunks),  # Stream video data in chunks
        status=200,
        mimetype='video/mp4',
        direct_passthrough=True
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
