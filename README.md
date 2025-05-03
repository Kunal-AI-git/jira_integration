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

## Available Endpoints(Example)
# Boards
GET /boards
List all available boards from your JIRA account.
Example Request:
http
GET /boards
Example Response:
json
[
  {
    "id": 1,
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/agile/1.0/board/1",
    "name": "SCRUM board",
    "type": "simple",
    "location": {
      "projectId": 10000,
      "displayName": "AI-Powered Technical Support Chatbot with RAG System (SCRUM)",
      "projectName": "AI-Powered Technical Support Chatbot with RAG System",
      "projectKey": "SCRUM",
      "projectTypeKey": "software",
      "avatarURI": "https://jkunal637-1745945445776.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10408?size=small",
      "name": "AI-Powered Technical Support Chatbot with RAG System (SCRUM)"
    },
    "isPrivate": false
  }
]

Description:
id: Board ID used in other endpoints (e.g. /boards/{board_id}/epics)
name: Display name of the board
projectKey: Project identifier used in CRUD and JQL queries
avatarURI: Icon shown for the project

## Epics and Stories
GET /boards/{board_id}/epics
Fetch all epics associated with a specific JIRA board.
Path Parameter:
board_id (integer): ID of the board (e.g., 1)
Example Request:
bash
curl -X 'GET' \
  'http://127.0.0.1:8000/boards/1/epics' \
  -H 'accept: application/json'
Example Response:
json
[
  {
    "id": 10000,
    "key": "SCRUM-1",
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/agile/1.0/epic/10000",
    "name": "",
    "summary": "Build the Core Chatbot System",
    "color": {
      "key": "color_7"
    },
    "issueColor": {
      "key": "purple"
    },
    "done": false
  },
  {
    "id": 10002,
    "key": "SCRUM-2",
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/agile/1.0/epic/10002",
    "name": "",
    "summary": "Build Frontend User Interface",
    "color": {
      "key": "color_7"
    },
    "issueColor": {
      "key": "purple"
    },
    "done": false
  }
]

Description:
key: Epic identifier (e.g., "SCRUM-1")
summary: Title of the epic
done: Indicates if the epic is completed
color: UI color key for the epic

## Stories Under an Epic
GET /epics/{epic_key}/stories
Fetch all stories under a specific epic.
Path Parameter:
epic_key (string): Key of the epic (e.g., SCRUM-1)
Example Request:
bash
curl -X 'GET' \
  'http://127.0.0.1:8000/epics/SCRUM-1/stories' \
  -H 'accept: application/json'
Example Response:
json
[
  {
    "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
    "id": "10049",
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issue/10049",
    "key": "SCRUM-15",
    "fields": {
      "summary": "Develop Chat API",
      "subtasks": []
    }
  },
  {
    "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
    "id": "10010",
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issue/10010",
    "key": "SCRUM-6",
    "fields": {
      "summary": "Set up Retrieval Augmented Generation (RAG) backend",
      "subtasks": []
    }
  }
]

Description:
key: Story issue key (e.g., SCRUM-6)
summary: Title/summary of the story
subtasks: Empty list or contains subtasks if any

## Tasks and Subtasks Under a Story
GET /stories/{story_key}/tasks
Fetch all tasks and subtasks linked to a specific story.
Path Parameter:
story_key (string): Key of the story (e.g., SCRUM-6)
Example Request
bash
curl -X 'GET' \
  'http://127.0.0.1:8000/stories/SCRUM-6/tasks' \
  -H 'accept: application/json'
Example Response
json
[
  {
    "id": "10033",
    "key": "SCRUM-7",
    "summary": "Set up Document Storage (e.g., FAISS, ElasticSearch, Pinecone)",
    "subtasks": [
      {
        "id": "10035",
        "key": "SCRUM-8",
        "summary": "Install FAISS and configure server"
      },
      {
        "id": "10037",
        "key": "SCRUM-9",
        "summary": "Define document schema for storage"
      },
      {
        "id": "10039",
        "key": "SCRUM-10",
        "summary": "Set up document indexing pipeline"
      }
    ]
  }
]

Description
key: Unique issue key for the task or subtask (e.g., SCRUM-7)
summary: Short title of the task or subtask
subtasks: A list of related subtasks under each task

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
# POST /issues
Create an issue
Params: project_key, summary, issue_type

Get All Issues in a Project
# GET /issues
Fetch all issues within a specific project.
Query Parameter:
project_key (string): Key of the project (e.g., SCRUM)
Example Request
bash
curl -X 'GET' \
  'http://127.0.0.1:8000/issues?project_key=SCRUM' \
  -H 'accept: application/json'
Example Response
json
[
  {
    "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
    "id": "10109",
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issue/10109",
    "key": "SCRUM-45",
    "fields": {
      "summary": "Show human support contact form",
      "subtasks": []
    }
  },
  {
    "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
    "id": "10107",
    "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issue/10107",
    "key": "SCRUM-44",
    "fields": {
      "summary": "Redirect User to Human Support",
      "subtasks": [
        {
          "id": "10109",
          "key": "SCRUM-45",
          "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issue/10109",
          "fields": {
            "summary": "Show human support contact form",
            "status": {
              "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/status/10000",
              "description": "",
              "iconUrl": "https://jkunal637-1745945445776.atlassian.net/",
              "name": "To Do",
              "id": "10000",
              "statusCategory": {
                "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/statuscategory/2",
                "id": 2,
                "key": "new",
                "colorName": "blue-gray",
                "name": "To Do"
              }
            },
            "priority": {
              "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/priority/3",
              "iconUrl": "https://jkunal637-1745945445776.atlassian.net/images/icons/priorities/medium_new.svg",
              "name": "Medium",
              "id": "3"
            },
            "issuetype": {
              "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issuetype/10005",
              "id": "10005",
              "description": "Subtasks track small pieces of work that are part of a larger task.",
              "iconUrl": "https://jkunal637-1745945445776.atlassian.net/2/universal_avatar/view/type/issuetype/avatar/10316?size=medium",
              "name": "Subtask",
              "subtask": true,
              "avatarId": 10316,
              "entityId": "60777707-018a-4142-8813-e0d8248be84a",
              "hierarchyLevel": -1
            }
          }
        }
      ]
    }
  }
]

Description
id: Unique identifier for the issue
key: Key for the issue (e.g., SCRUM-45)
summary: A brief summary of the issue
subtasks: A list of subtasks related to the issue (if any)
status: Current status of the issue
priority: Priority level of the issue
issuetype: Type of the issue (e.g., Task, Subtask)

# PUT /issues/{issue_id}
PUT /issues/{issue_id}
Update the summary of an existing issue.
Path Parameter:
issue_id (string): The ID of the issue to be updated.
Request Body:
summary (string): New summary of the issue.
Example Request
bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/issues/10109' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "summary": "Updated summary for human support contact form"
  }'
Example Response
json
{
  "id": "10109",
  "self": "https://jkunal637-1745945445776.atlassian.net/rest/api/3/issue/10109",
  "key": "SCRUM-45",
  "fields": {
    "summary": "Updated summary for human support contact form"
  }
}

# DELETE /issues/{issue_id}
DELETE /issues/{issue_id}
Delete an issue by its ID.
Path Parameter:
issue_id (string): The ID of the issue to be deleted.
Example Request
bash
curl -X 'DELETE' \
  'http://127.0.0.1:8000/issues/10109' \
  -H 'accept: application/json'
Example Response
json
{
  "message": "Issue with ID 10109 has been deleted successfully."
}

Description
PUT /issues/{issue_id}: Used to update the summary of an existing issue. Requires providing the issue_id in the path and a new summary in the request body.
DELETE /issues/{issue_id}: Used to delete an issue. Requires providing the issue_id in the path

## Output File
jira_hierarchy.json
Created when calling GET /hierarchy/save. Contains full board structure in JSON.

## License ##
This project is licensed under the MIT License.