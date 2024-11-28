from flask import Flask, Response, request
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import uuid

app = Flask(__name__)

# Connect to Cassandra
def get_cassandra_session():
    cluster = Cluster(['172.17.0.1'])  # Replace with Cassandra Docker IP
    session = cluster.connect('media_keyspace')
    return session

# Fetch video chunks from Cassandra
def fetch_video_chunks(video_id):
    session = get_cassandra_session()
    query = SimpleStatement("""
        SELECT chunk_index, chunk_data FROM video_chunks WHERE video_id = %s
    """)
    rows = session.execute(query, (uuid.UUID(video_id),))
    chunks = sorted(rows, key=lambda row: row.chunk_index)  # Ensure chunks are in order
    return [chunk.chunk_data for chunk in chunks]

# Stream video route
@app.route('/video/<video_id>')
def stream_video(video_id):
    chunks = fetch_video_chunks(video_id)
    if not chunks:
        return "Video not found", 404

    def generate():
        for chunk in chunks:
            yield chunk

    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
