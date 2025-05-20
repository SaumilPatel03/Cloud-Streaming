# Use the official Nginx image from Docker Hub as a base image
FROM nginx:latest

# Copy your custom Nginx configuration file into the container
COPY server_nginx.conf /etc/nginx/nginx.conf

# Optionally, copy your web content (if you're serving static files)
# COPY ./html /usr/share/nginx/html

# Expose port 8080 (or whichever port your Nginx is listening on)
EXPOSE 8080

# The default command is already set to start Nginx, so no need to add it explicitly.
