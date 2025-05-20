from flask import Flask, jsonify, request, abort
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Initialize Flask app
app = Flask(_name_)

# Cassandra connection setup (modify with your details)
def get_cassandra_session():
    cluster = Cluster(['172.17.0.1'])  # Replace with your Cassandra node IPs
    session = cluster.connect('media_keyspace')  # Connect to the media_keyspace
    return session

# Check if Cassandra is reachable
def check_cassandra():
    try:
        session = get_cassandra_session()
        session.execute('SELECT now() FROM system.local')
        return True
    except Exception as e:
        print("Error connecting to Cassandra:", e)
        return False

# Home route
@app.route('/')
def index():
    return "Flask Backend is running, connected to Cassandra!"

# Endpoint to get media items
@app.route('/media/<media_id>', methods=['GET'])
def get_media(media_id):
    session = get_cassandra_session()
    query = f"SELECT * FROM media WHERE media_id = {media_id};"
    
    try:
        result = session.execute(query)
        if result:
            return jsonify(result[0]._asdict())  # Convert result to a dictionary and return as JSON
        else:
            abort(404, description="Media not found")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create new media entry
@app.route('/media', methods=['POST'])
def create_media():
    if not request.json or 'media_id' not in request.json:
        abort(400, description="Bad Request: Missing media_id")

    media_data = request.json
    media_id = media_data.get('media_id')
    title = media_data.get('title')
    genre = media_data.get('genre')
    release_year = media_data.get('release_year')
    
    session = get_cassandra_session()
    
    query = f"""
        INSERT INTO media (media_id, title, genre, release_year)
        VALUES ({media_id}, '{title}', '{genre}', {release_year});
    """
    
    try:
        session.execute(query)
        return jsonify({"message": "Media item created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Check the Cassandra connection status
@app.route('/check_cassandra', methods=['GET'])
def check_cassandra_status():
    if check_cassandra():
        return jsonify({"message": "Cassandra is connected!"}), 200
    else:
        return jsonify({"message": "Cassandra connection failed!"}), 500

# Start the Flask app
if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000)  # Runs on port 5000 by default
