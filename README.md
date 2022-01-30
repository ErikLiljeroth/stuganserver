# Streamlit app to store and display measurements of temperature and relative humidity

The system consists of a streamlit app and a mariadb/mysql database running on separate Docker containers on a shared Docker network.  Made to run on Raspberry Pi and be placed below the floor of the author's cabin to monitor cabin foundation health. 

![image of app running](/images/app_overview.png)

## Installation
Pull any hardware-compatible MariaDB image from Docker. MariaDB For Raspberry-Pi: https://hub.docker.com/r/jsurf/rpi-mariadb/

1. Clone this repo
2. create `secrets.toml` in directory `.streamlit` and specify the following information: 
```
# .streamlit/secrets.toml

[mysql]
host = [...]# Name of Database docker image, or localhost if no container 
port = [...]# Port of database, default for mysql/mariadb is 3306
database = [...]# Name of database, "stugandata" in this project
user = [...]# Name of db-user
password = [...]# Password of db-user
```
3. create .env-file repository root directory and specify the following information:
```
DB_ROOT_PASSWORD=[password of db-root]
COMPOSE_PROJECT_NAME=[name of docker network]
```
4. Build the Streamlit-app image from Dockerfile 
>`docker build -t stuganapp:latest .`
5. In file `docker-compose.yml`, change database image name to match used (system-compatible) image
>
```
[...]
stugandb:
    image: [db image name]
[...]
```

6. Create required volumes for persistent db storage
>`docker volume create stugan-data`

>`docker volume create mariadb_config`
7. Compose system and run containers
>`docker-compose up -d` 