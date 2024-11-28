from flask import Flask, Response, request
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import io
import uuid
import re

app = Flask(__name__)

# 
def get_cassandra_session():
    cluster = Cluster(['172.17.0.1'])  # Replace with the correct Cassandra IP
    session = cluster.connect('media_keyspace')  # Connect to the keyspace
    return session

# Fetch video data from Cassandra
def fetch_video(video_id):
    session = get_cassandra_session()
    query = SimpleStatement("""
        SELECT video_data, video_name FROM videos WHERE video_id = %s
    """)
    rows = session.execute(query, (uuid.UUID(video_id),))
    return rows.one()

# Stream video route
@app.route('/video/<video_id>')
def stream_video(video_id):
    video = fetch_video(video_id)
    if not video:
        return "Video not found", 404

    video_data = video.video_data
    start = 0
    end = len(video_data) - 1

    # Parse the "Range" header from the request
    range_header = request.headers.get('Range', None)
    if range_header:
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start = int(range_match.group(1))
            end = range_match.group(2)
            if end:
                end = int(end)
            else:
                end = len(video_data) - 1

    # Create the partial video data to send
    chunk = video_data[start:end + 1]

    # Generate the response
    response = Response(
        io.BytesIO(chunk),  # Serve the chunk
        status=206 if range_header else 200,
        mimetype='video/mp4',
        direct_passthrough=True
    )
    response.headers.add('Content-Range', f'bytes {start}-{end}/{len(video_data)}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(len(chunk)))
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
