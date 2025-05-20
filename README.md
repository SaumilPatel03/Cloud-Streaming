# Cloud-Streaming
Cloud-Streaming is a Python-based project designed to facilitate seamless streaming of data to the cloud. This project leverages Docker for containerization, ensuring a consistent and reproducible environment for deployment.

## Features

- **High Performance:** Optimized for efficient data streaming.
- **Scalability:** Easily scales to handle large amounts of data.
- **Dockerized:** Simplified deployment using Docker.

## Technologies Used

- **Python:** The main programming language used in this project.
- **Flask:** Lightweight web framework used for the application server.
- **Docker:** Used for containerization to ensure consistency across different environments.
- **Nginx:** Used as a proxy server.

## Project Structure

The repository is organized as follows:

-   `app/`: Contains the main application code.
    -   `app/main.py`: The main Flask application entry point.
    -   `app/stream_routes.py`: Handles video streaming logic.
    -   `app/server/`: Contains server-specific configurations (e.g., Nginx, Dockerfile).
    -   `app/client/`: Contains client-side components or code.
-   `docs/`: Contains documentation files.
    -   `docs/cassandra_configuration.txt`: Guide for Cassandra configuration.
    -   `docs/cassandra_installation_guide.txt`: Guide for installing Cassandra.
-   `scripts/`: Contains utility and helper scripts.
    -   `scripts/upload_chunked_video.py`: Script to chunk videos and upload them with metadata to Cassandra.
    -   `scripts/upload_video_blob.py`: Script to upload entire video files as blobs to Cassandra.
