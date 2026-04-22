# FILES WITH BUGS AND THEIR FIXES
1. api/requirements.txt
    - specific versions of the requirements were not specified in the file
    - the file missed some vital packages  
Fixes:
        * did a pip install to have the necessary packages on my local machine and
            pip freeze > requirements.txt to update the file
2. api/main.py
    - wrong redis connection host (localhost fails in docker)
    - the application was binding to 127.0.0.1 which made the frontend unable to access it
    - no error status codes in error return response
    - no healthcheck endpoint  
Fixes:
        * replaced it with the env variable
        * added error code for error response
        * added health check endpoint
3. frontend/yarn-lock.json
    - file was missing  
Fixes:
        * cd into frontend directory and create using yarn install
4. frontend/app.js
    - the api_url and port were hardcoded 
    - no error handling  
Fixes: 
        * replaced the url and port with env variables
        * handled 404 no job found error
5. .dockerignore and .gitignore
    - no docker ignore file
    - no git ignore file  
Fixes: 
        * added .gitignore file to prevent .env from being copied to git
        * added .dockerignore files to each service to prevent secrets and build files from being copied into the containers  
6. frontend/package.json
    - No license field  
Fixes: 
        * added license field to remove the docker warning
7. worker/worker.py
    - redis screts were hardcoded
    - no error handling  
Fixes:
        * used env variables
        * handled error incase any exception is thrown so the worker doesn't crash 
8. docker files
    - missing Dockerfile and docker-compose.yml files  
Fixes:
    - added dockerfiles for each service