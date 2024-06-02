
# Social Networking Application

This project is an implementation of a social networking API using Django Rest Framework. It provides various functionalities for users to interact with the platform, including user authentication, searching for other users, sending/accepting/rejecting friend requests, and managing friends.




## Features

- User Authentication: Users can sign up and log in using their email and password.
- User Search: Search for other users by email or name, with pagination support.
- Friend Management: Send, accept, or reject friend requests, and list friends and pending friend requests.



## Installation

Clone the repo:

```bash
  git clone https://github.com/subashkj005/Social-Networking-API.git
```
Create a virtual enviroment:
```bash
  python -m venv venv
```
Activate the enviroment:
```bash
  venv/Scripts/activate
```
Install the requirements.txt file:
```bash
  pip install -r requirements.txt
```
Direct the terminal to the root directory (where manage.py file lies) of the application:
```bash
  cd .\socialmediaapi\
```
Run the migrations:
```bash
  python manage.py makemigrations
  python manage.py migrate
```
Run:
```bash
  python manage.py runserver
```

Congratulations =) !!! The App should be running in [localhost:8000](http://localhost:8000/)
    
## Run the application using Docker and Docker-compose

1. Open the terminal in where the docker-compose.yml file lies.
2. To create the docker image locally

```bash
docker-compose build
```
3. After building image, run the image using docker-compose.
```
docker-compose up -d
```
4. Congratulations, Now the application will be available on [localhost:8000](http://localhost:8000/)
## Documentation

Detailed documentation of each API endpoint can be found in the Postman collection provided in the repository. Also the link to the documentation is also providing [here](https://documenter.getpostman.com/view/28819113/2sA3Qwb9zV).


