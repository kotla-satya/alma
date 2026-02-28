
# To run unit tests
 python -m pytest tests/ -v

# Setup Instructions
install Docker locally


# create the server
Download the repo
Create a .env file
Change the .env file to your liking mainly ADMIN_EMAIL and ADMIN_PASSWORD to setup the admin user/default attorney
Register in resend.com and add valid email domains in DOMAINS or else you will see error in log file.

# To start the server, Run the following commands
docker compose build
docker compose up -d

# To stop the server
docker compose down # stop the server, keep the DB
docker-compose down -v       # stop + wipe DB

Once Docker is up and running, 
Run docker ps to check the status of the containers. you should see the server running
(.venv) satya Alma % docker ps     
CONTAINER ID   IMAGE                                             COMMAND                   CREATED          STATUS                    PORTS                                                        NAMES
08ac1bc53996   alma-app                                          "sh -c 'python scrip…"    23 minutes ago   Up 23 minutes             0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp                  alma-app-1
1a39e6b6fe65   postgres:16-alpine                                "docker-entrypoint.s…"    23 minutes ago   Up 23 minutes (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp                  alma-db-1

## Access Swagger UI
you can access the API at http://localhost:8000/docs

you can try accessing the api's here or use curl. For login, use email and password from .env file

# Login with test user, the user email and password can be changed in .env file
Login (get a JWT):
  curl -X POST http://localhost:8000/auth/login \
    -d "username=kotla.satya@gmail.com&password=changeme"

Sample response
{
    "access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjJlMzVkNS1jOTQ5LTQ0MjQtOWZmZS0yOWRkNWQxNzlkY2YiLCJyb2xlIjoiQVRUT1JORVkiLCJleHAiOjE3NzIzMjIwNTN9.p2f11PyoYwrBha7fXng1YL47SJdyLz5SkXdVkPsWQWw",
    "token_type":"bearer"
}   

List leads (requires JWT):
  curl http://localhost:8000/leads/ \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjJlMzVkNS1jOTQ5LTQ0MjQtOWZmZS0yOWRkNWQxNzlkY2YiLCJyb2xlIjoiQVRUT1JORVkiLCJleHAiOjE3NzIzMjIwNTN9.p2f11PyoYwrBha7fXng1YL47SJdyLz5SkXdVkPsWQWw"

# Create a lead
  curl -X POST http://localhost:8000/leads/ \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjJlMzVkNS1jOTQ5LTQ0MjQtOWZmZS0yOWRkNWQxNzlkY2YiLCJyb2xlIjoiQVRUT1JORVkiLCJleHAiOjE3NzIzMjIwNTN9.p2f11PyoYwrBha7fXng1YL47SJdyLz5SkXdVkPsWQWw"
    -F "first_name=Jane" \
    -F "last_name=Doe" \
    -F "email_id=kotla.satya+7@gmail.com" \
    -F "resume=@/path/to/resume.pdf"



