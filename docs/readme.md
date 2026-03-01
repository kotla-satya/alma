
## Project Structure

```
Alma/
├── app/
│   ├── main.py                        # FastAPI app factory, routers, APScheduler lifespan
│   ├── config.py                      # Pydantic settings (reads from .env)
│   ├── database.py                    # Async SQLAlchemy engine + get_db dependency
│   ├── dependencies/
│   │   └── auth.py                    # JWT helpers, get_current_user, require_attorney
│   ├── models/
│   │   ├── base.py                    # SQLAlchemy DeclarativeBase
│   │   ├── user.py                    # UserRole, User
│   │   ├── lead.py                    # LeadState, Lead
│   │   └── notification.py            # NotificationType, LeadNotification
│   ├── routers/
│   │   ├── auth.py                    # POST /auth/login
│   │   ├── leads.py                   # Lead CRUD + resume download
│   │   └── users.py                   # POST /user
│   ├── schemas/
│   │   ├── lead.py                    # LeadCreate, LeadRead, LeadUpdate
│   │   └── user.py                    # UserCreate, UserRead, TokenResponse
│   └── services/
│       ├── lead_service.py            # Lead business logic
│       ├── user_service.py            # User business logic
│       ├── email_service.py           # Resend email sender
│       └── notification_service.py    # Cron job — processes pending notifications
├── alembic/
│   ├── env.py                         # Alembic config (pulls DB URL from settings)
│   └── versions/                      # Migration files
├── docs/
│   ├── Design Doc.md
│   └── readme.md
├── scripts/
│   └── init_db.py                     # Creates tables + seeds roles, states, default attorney
├── tests/
│   ├── conftest.py                    # SQLite in-memory fixtures, seeded test DB
│   └── test_leads.py                  # Lead API + notification service tests
├── .env.example                       # Environment variable template
├── .gitignore
├── alembic.ini
├── docker-compose.yml                 # app + postgres services
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

## Database Schema (ERD)

```mermaid
erDiagram
    USER_ROLE {
        string role_id PK "ATTORNEY | PARA_LEGAL | CLERK"
        string role_name
        datetime created_at
        datetime updated_at
    }

    USER {
        uuid id PK
        string name
        string email UK
        string hashed_password
        string user_role_id FK
        bool is_active
        datetime created_at
        datetime updated_at
        datetime deactivated_at
    }

    LEAD_STATE {
        string lead_state_id PK "PENDING | REACHED_OUT"
        string lead_state_name
        datetime created_at
        datetime updated_at
    }

    LEAD {
        uuid id PK
        string first_name
        string last_name
        string email_id UK
        blob resume
        string resume_filename
        string lead_state_id FK
        uuid handled_by_user_id FK
        string attorney_notes
        datetime created_at
        datetime updated_at
    }

    NOTIFICATION_TYPE {
        string notification_type_id PK "email_new_lead_submission"
        string notification_type_name
    }

    LEAD_NOTIFICATION {
        uuid id PK
        uuid lead_id FK
        string notification_type_id FK
        bool is_lead_notified
        bool is_attorney_notified
        datetime lead_notified_at
        datetime attorney_notified_at
        datetime created_at
        datetime updated_at
    }

    USER_ROLE ||--o{ USER : "assigned to user_role_id"
    USER ||--o{ LEAD : "handles"
    LEAD_STATE ||--o{ LEAD : "state types"
    LEAD ||--|| LEAD_NOTIFICATION : "triggers"
    NOTIFICATION_TYPE ||--o{ LEAD_NOTIFICATION : "notification types"
```

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

Once Docker is up and running, Run docker ps to check the status of the containers. you should see the server running

use `docker ps` and see alma-app-1 and alma-db-1 running


## Access Swagger UI
you can access the API at http://localhost:8000/docs

you can try accessing the api's here or use curl. For login, use email and password from .env file

# Login with test user, the user email and password can be changed in .env file
Login (get a JWT):
  curl -X POST http://localhost:8000/auth/login \
    -d "username=kotla.satya@gmail.com&password=changeme"

Sample response
{
    "access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
    "token_type":"bearer"
}   

List leads (requires JWT):
  curl http://localhost:8000/leads/ \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Create a lead
  curl -X POST http://localhost:8000/leads/ \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    -F "first_name=Jane" \
    -F "last_name=Doe" \
    -F "email_id=kotla.satya+7@gmail.com" \
    -F "resume=@/path/to/resume.pdf"



