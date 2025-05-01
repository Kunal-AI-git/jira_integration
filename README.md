## JIRA Integration API
A FastAPI-based backend to interact with JIRA's REST APIs. This project allows you to:
- Fetch Agile boards, epics, stories, and tasks
- Manage project users and roles
- Create, update, delete JIRA issues
- View project hierarchy (Board → Epic → Story → Task)
- Export hierarchy to JSON
- Fully integrated with Swagger UI for API testing

## Features

| Feature                     | Description                         
|-----------------------------|---------------------------------------------------|
| `/boards`                   | Get all boards in your JIRA workspace             |
| `/boards/{id}/epics`        | Fetch epics under a specific board                |
| `/epics/{key}/stories`      | Fetch stories under an epic                       |
| `/stories/{id}/tasks`       | Fetch subtasks of a story                         |
| `/teams/project`            | Get all users in a JIRA project with roles        |
| `/issues (POST/PUT/DEL)`    | Create, update, delete JIRA issues                |
| `/hierarchy`                | View complete project hierarchy                   |
| `/hierarchy/save`           | Save the full hierarchy to `jira_hierarchy.json`  |

## Setup Instructions

1. Create a virtual environment and install dependencies
   ```bash
   pip install -r requirements.txt
   python -m venv venv

2. Create a .env file in the project root
ini
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-generated-token
JIRA_DOMAIN=your-domain.atlassian.net

**Replace your-email@example.com with your Atlassian email**
**Replace your-domain with your JIRA workspace domain**

## How to get your JIRA API Token ##
1. Log into https://id.atlassian.com/manage-profile/security/api-tokens
2. Click Create API token
3. Copy the token and paste it into your .env file as JIRA_API_TOKEN

## How to Get JIRA_DOMAIN
1. Create an Atlassian Account
>> Go to: https://id.atlassian.com/signup
>> Sign up using your email address.

2. Create a Free JIRA Site
>> Visit: https://www.atlassian.com/software/jira/free
>> Click "Try it free" for Jira Software.
>> Choose Cloud.
>> Set your site name → this becomes your domain:
Example: If you enter myproject, your domain will be:
myproject.atlassian.net

3. Create a Project
>> After logging in, click "Create Project".
>> Choose a Scrum or Kanban template (Agile boards).
>> Give it a name like ESA or KAN (your project key).

## Running the Server ##
Start the FastAPI server:
bash
uvicorn jira:app --reload

Visit the Swagger UI at:
bash
http://localhost:8000/docs
Or the ReDoc UI:
bash
http://localhost:8000/redoc

## Example .env file ##
ini
JIRA_EMAIL=your_mail_id@example.com
JIRA_API_TOKEN=your-real-api-token
JIRA_DOMAIN=yourteam.atlassian.net

## API Testing (Swagger) ##
Use Swagger UI to test endpoints easily. It shows:
1. All available routes
2. Input parameters and models
3. Real-time responses
4. Integrated Try-it-out feature

## Available Endpoints
# Boards
GET /boards
List all JIRA boards

GET /boards/{board_id}/epics
List epics on a specific board

## Epics and Stories
GET /epics/{epic_key}/stories
Get stories under an epic

GET /stories/{story_key}/tasks
Get tasks and subtasks related to a story

## Full Hierarchy
GET /hierarchy
Fetch entire board → epic → story → task structure

GET /hierarchy/save
Save the full hierarchy to jira_hierarchy.json

## JQL & Project Users
GET /issues
Search issues by JQL (uses project key)

GET /teams/project?project_key=KAN
List users in a given JIRA project

## CRUD Operations
POST /issues
Create an issue
Params: project_key, summary, issue_type

GET /issues/{issue_key}
Get issue details

PUT /issues/{issue_id}
Update an issue’s summary

DELETE /issues/{issue_id}
Delete an issue

## Output File
jira_hierarchy.json
Created when calling GET /hierarchy/save. Contains full board structure in JSON.

## License ##
This project is licensed under the MIT License.