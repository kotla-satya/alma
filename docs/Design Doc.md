App to support taking leads as input by prospects and ability for attorney’s to manage the life cycle of prospects.

Prospects can be any users in the world.

Types of personas/users

- Attorneys
- Prospects

**ASK**: Build backend service/API’s to support these features

**Assumptions**

- Lead and Prospect is 1:1
- Leads can not be updated once submitted
- Once lead is submitted, all the emails are sent to **same attorney(one fixed instead of dynamic)** and corresponding prospect
- Attorney **can not** update lead details except the lead state and notes field

**Design choices**

- Using Database to store the resume directly in DB, in prod this can be stored in S3 and save reference to it in DB
- No size restriction on the document upload
- No rate limiting on lead creation
- Updates can not be made to lead
- Resume uploaded can be viewed on demand
- Default Admin/Attorney user is created using script on setup of the app
- Based on time permitting
    - support for logging and metrics
    - Attorney/App users CRUD support

**Database Schema**

**User**

- id (uuid)
- Name
- Email
- User_Role_ID (Default Attorney)
- is_active
- Created_at
- updated_at
- deactivated_at

**User_Role (All users have same access controls for now)**

- role_id **(Attorney, Para_legal, Clerk etc)**
- role_name
- created_at
- updated_at

**Lead (to store leads provided by prospect)**

- id (UUID)
- first_name
- last_name
- email_id (unique)
- resume (BLOB)
- created_at
- updated_at
- lead_state_id (Default Pending)
- handled_by_user_id (when in reached_out state, this should have user id value) None by default
- attorney_notes (optional for storing any details)

**Lead_Notification (This can be extended to other types of notifications)**

- lead_id
- notification_type_id (Default email_new_lead_submission )
- created_at
- updated_at
- is_lead_notified
- is_attorney_notified
- attorney_notified_at
- lead_notified_at

**Lead_State**

- lead_state_id (PENDING, REACHED_OUT)
- lead_state_name (Pending, Reached Out)
- created_at
- updated_at

**Notification_Type**

- notification_type_id (`email_new_lead_submission` etc)
- notification_type_name

**API**

**CRUD /leads**

POST /lead (publicly available not auth protected). Default Admin attorney is assigned on creation.

GET /leads/ (Auth Protected - valid user)

GET /leads/{id} (Auth Protected - valid user)

PATCH /leads/{id} (Auth Protected - valid user) - to update the lead_state only

GET /leads/{id}/resume (Auth Protected - valid user)

**CRUD /user (To manage admins/attorney/internal users)**

Based on time permitting do this, only attorney’s can manage other users

POST /user

**Utilities/Service**

Email Service to send emails

**Cron Job** 

Runs every few minutes say 5mins, Emails the prospect and attorney for lead entries in `lead_notifications` table, once emails are sent the corresponding columns are updated.

An entry is made in to lead_notifications table on creation of lead with lead id and notification_type with `email_new_lead_submission`.

**Tech Stack**

- Python 3.12, Postgres as DB
- FAST API
- SQL Alchemy as ORM
- Alembic for database schema maintenance
- JWT for auth
- Docker
- pytests for unit test using sql lite (based on time permitting)
- Resend [`resend.com/`](http://resend.com/) - for Email