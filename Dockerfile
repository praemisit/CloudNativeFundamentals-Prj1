# Set the base image
FROM python:2.7

# Set a key-value label for the Docker image
LABEL maintainer="praesimit"

# copy the techtrends project files to the container 
# filesystem.
COPY techtrends /app

#  defines the working directory within the container
WORKDIR /app

# define the port
EXPOSE 3111

# run commands within the container.
RUN pip install -r requirements.txt
# provide a command to run on container start.
# For example, start the `app.py` application.
CMD [ "python", "init_db.py" ]
CMD [ "python", "app.py" ]
