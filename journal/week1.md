# Week 1 — App Containerization

## Required Homework/Tasks

### Containerize Application (Dockerfiles, Docker Compose)

#### Containerize Backend

1. Create a Dockerfile under `backend-flask/Dockerfile`.
    ```
    FROM python:3.10-slim-buster

    # Inside Container
    # make a new folder inside container
    WORKDIR /backend-flask

    # Outside Container -> Inside Container
    # this contains the libraries to be installed to run the app
    COPY requirements.txt requirements.txt

    # Inside Container
    # Install the python libraries used for the app
    RUN pip3 install -r requirements.txt

    # Outside Container -> Inside Container
    # means everything in the current directory
    # first period /backend-flask (outside container)
    # second period /backend-flask (inside container)
    COPY . .


    # Set Environment Variables
    # Inside Container and will remain set when the container is running
    ENV FLASK_ENV=development

    EXPOSE ${PORT}
    CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
    ```
2. Build container.
    ```
    docker build -t  backend-flask-image ./backend-flask
    ```
    ![Docker Build](assets2/week-1/docker-build.png)
    
    ![Docker Image](assets2/week-1/docker-images.png)
3. Run container.
    ```
    export FRONTEND_URL="*"
    export BACKEND_URL="*"
    docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' backend-flask-image
    ```
    ![Docker Run](assets2/week-1/docker-run.png)
    
    To unset environment variable.
    ```
    unset FRONTEND_URL="*"
    unset BACKEND_URL="*"
    ```
    
    To run container in background
    ```
    docker container run --rm -p 4567:4567 -d backend-flask
    ```
4. Check whether it's working by appending `/api/message_groups`.
   ![Backend Flask GET](assets2/week-1/backend-api-testing.png)

#### Containerize Frontend

1. Run NPM Install.
   We have to run NPM Install before building the container since it needs to copy the contents of node_modules
   ```
   cd frontend-react-js
   npm i
   ```
2. Create a Dockerfile under `frontend-react-js/Dockerfile`.
   ```
    FROM node:16.18

    ENV PORT=3000

    COPY . /frontend-react-js
    WORKDIR /frontend-react-js
    RUN npm install
    EXPOSE ${PORT}
    CMD ["npm", "start"]
   ```
3. Build Container.
   ```
   docker build -t frontend-react-js-image ./frontend-react-js
   ```
   ![Docker Build](assets2/week-1/docker-frontend-build.png)
   
   ![Docker Image](assets2/week-1/docker-frontend-images.png)
4. Run Container.
   ```
   docker run -p 3000:3000 -d frontend-react-js-image
   ```
   ![Docker Run](assets2/week-1/docker-frontend-run.png)
5. Test the page.
   ![Frontend Page](assets2/week-1/frontend-testing.png)
