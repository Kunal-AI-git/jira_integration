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

## Overview
This FastAPI backend connects to JIRA Cloud REST API and provides a simplified way to manage:

📋 Boards

🧩 Epics

🧶 Stories

✅ Tasks

🧵 Subtasks

👥 Project Team Members

1. List All Boards
Endpoint: GET /boards
Purpose: See all JIRA boards available.

 Input:
No input required.

 Output:
json

[
  {
    "id": 1,
    "name": "SCRUM board",
    "location": {
      "projectKey": "SCRUM"
    }
  }
]
Use the id for fetching epics or stories. Use projectKey for issues and team.

2. Get All Epics in a Board
Endpoint: GET /boards/{board_id}/epics
Purpose: Get all epics from a selected board.

 Input:
board_id = 1 (from /boards)

 Output:
json

[
  {
    "key": "SCRUM-1",
    "summary": "Build the Core Chatbot System"
  },
  {
    "key": "SCRUM-2",
    "summary": "Build Frontend User Interface"
  }
]
3. Get All Stories Under an Epic
Endpoint: GET /epics/{epic_key}/stories
Purpose: View stories grouped under an epic.

 Input:
epic_key = SCRUM-1

 Output:
json

[
  {
    "key": "SCRUM-6",
    "fields": {
      "summary": "Set up RAG backend"
    }
  }
]
4. Get Tasks & Subtasks Under a Story
Endpoint: GET /stories/{story_key}/tasks
Purpose: See breakdown of a story into smaller tasks/subtasks.

 Input:
story_key = SCRUM-6

 Output:
json

[
  {
    "key": "SCRUM-7",
    "summary": "Set up Document Storage",
    "subtasks": [
      {
        "key": "SCRUM-8",
        "summary": "Install FAISS"
      },
      {
        "key": "SCRUM-9",
        "summary": "Define document schema"
      }
    ]
  }
]
5. View Full Hierarchy
Endpoint: GET /hierarchy
Purpose: One-shot fetch of board → epic → story → task → subtask.

 Input:
No input needed.

 Output:
json

{
  "boards": [
    {
      "id": 1,
      "name": "SCRUM board",
      "epics": [
        {
          "key": "SCRUM-1",
          "summary": "Build Chatbot",
          "stories": [
            {
              "key": "SCRUM-6",
              "summary": "Set up backend",
              "tasks": [
                {
                  "key": "SCRUM-7",
                  "summary": "Doc Storage",
                  "subtasks": [...]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
6. Save Hierarchy
Endpoint: GET /hierarchy/save
Purpose: Saves the full hierarchy to a JSON file.

7. Search All Issues by Project Key
Endpoint: GET /issues?project_key=SCRUM
Purpose: View all issues (tasks/subtasks/stories) in a project.

 Input:
project_key = SCRUM

 Output:
json

[
  {
    "key": "SCRUM-44",
    "summary": "Redirect User",
    "subtasks": [
      {
        "key": "SCRUM-45",
        "summary": "Show contact form"
      }
    ]
  }
]
8.  Get All Project Users
Endpoint: GET /teams/project?project_key=SCRUM
Purpose: List all users in a JIRA project.

## CRUD Operations
# Create Issue
POST /issues

# Input:
json

{
  "project_key": "SCRUM",
  "summary": "New Feature XYZ",
  "issue_type": "Task"
}
# Output:
json

{
  "key": "SCRUM-50",
  "summary": "New Feature XYZ"
}

# Update Issue Summary
PUT /issues/{issue_id}

# Input:
issue_id = 10109

Request Body:
json

{
  "summary": "Updated summary for human support form"
}
# Output:
json

{
  "id": "10109",
  "summary": "Updated summary for human support form"
}

# Delete Issue
DELETE /issues/{issue_id}

# Input:
issue_id = 10109

# Output:
json

{
  "message": "Issue with ID 10109 has been deleted successfully."
}

## Summary of What You Need To Know:

|Task                    |   Endpoint Example	                  |     Input Example         |
|------------------------|--------------------------------------|---------------------------|
|Get all boards	         |     GET /boards                      |   	None                  |
|Get epics from board	   |     GET /boards/1/epics	            |     board_id = 1          |
|Get stories in an epic	 |     GET /epics/SCRUM-1/stories	      |      epic_key = SCRUM-1   |
|Get tasks of a story	   |     GET /stories/SCRUM-6/tasks	      |      story_key = SCRUM-6  |
|Get full hierarchy	     |     GET /hierarchy	                  |      None                 |
|Save hierarchy to file	 |     GET /hierarchy/save	            |      None                 |
|Update issue summary	   |     PUT /issues/10109	              |      summary in body      |
|Delete an issue	       |       DELETE /issues/10109	          |        issue_id = 10109   |

## Output File
jira_hierarchy.json
Created when calling GET /hierarchy/save. Contains full board structure in JSON.

## License ##
This project is licensed under the MIT License.