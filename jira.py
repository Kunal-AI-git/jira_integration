import os
import json
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# FastAPI app initialization
app = FastAPI(
    title="JIRA Integration API",
    description="Fetch and manage JIRA Boards, Epics, Stories, Tasks"
)

# JIRA Configuration
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = f"https://{os.getenv('JIRA_DOMAIN')}"

# ---------------------- HELPERS ----------------------

def get_jira_session():
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN), {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def safe_request(method, url, headers, auth, **kwargs):
    try:
        response = requests.request(method, url, headers=headers, auth=auth, **kwargs)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        response.raise_for_status()
        return response.json() if response.content else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during {method.upper()} request to {url}: {str(e)}")

# ---------------------- SEARCH ISSUES (Added) ----------------------

def search_issues(jql: str, max_results: int = 50):
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "maxResults": max_results,
        "fields": "summary,subtasks"
    }
    return safe_request("GET", url, headers, auth, params=params).get("issues", [])

# ---------------------- DYNAMIC FIELD SUPPORT ----------------------

_epic_link_field_id_cache = None

def get_epic_link_field_id():
    global _epic_link_field_id_cache
    if _epic_link_field_id_cache:
        return _epic_link_field_id_cache

    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/api/3/field"
    fields = safe_request("GET", url, headers, auth)

    for field in fields:
        if field.get("name", "").lower() == "epic link":
            _epic_link_field_id_cache = field["id"]
            return _epic_link_field_id_cache

    raise HTTPException(status_code=500, detail="Could not find 'Epic Link' field in JIRA.")

# ---------------------- MODELS ----------------------

class TaskModel(BaseModel):
    id: str
    key: str
    summary: str

class StoryModel(BaseModel):
    id: str
    key: str
    summary: str
    tasks: List[TaskModel]

class EpicModel(BaseModel):
    id: str
    name: str
    stories: List[StoryModel]

class BoardModel(BaseModel):
    id: int
    name: str
    epics: List[EpicModel]

# ---------------------- READ ENDPOINTS ----------------------

@app.get("/boards", summary="Fetch all boards")
def fetch_boards():
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    return safe_request("GET", url, headers, auth).get("values", [])

@app.get("/boards/{board_id}/epics", summary="Fetch epics for a board")
def fetch_epics(board_id: int):
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/epic"
    return safe_request("GET", url, headers, auth).get("values", [])

@app.get("/epics/{epic_key}/stories", summary="Fetch stories for an epic")
def fetch_stories(epic_key: str):
    jqls = []

    # Try team-managed query first
    jqls.append(f'parent = "{epic_key}"')

    # Then try company-managed query if Epic Link field is found
    try:
        epic_link_field = get_epic_link_field_id()
        jqls.append(f'"{epic_link_field}" = "{epic_key}"')
    except:
        pass  # Ignore error and rely on parent-based lookup

    for jql in jqls:
        issues = search_issues(jql)
        if issues:
            return issues

    raise HTTPException(
        status_code=404,
        detail=f"No stories found for epic '{epic_key}'. Tried JQLs: {jqls}"
    )

@app.get("/stories/{story_key}/tasks", summary="Fetch tasks and subtasks linked to a story")
def fetch_tasks_and_subtasks(story_key: str):
    auth, headers = get_jira_session()

    # Fetch story issue details
    issue_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{story_key}"
    issue_data = safe_request("GET", issue_url, headers, auth)

    # Get linked issues
    issue_links = issue_data.get("fields", {}).get("issuelinks", [])
    print(f"[DEBUG] Issue links for {story_key}: {issue_links}")

    tasks = []

    for link in issue_links:
        # Check for 'relates to' or any link
        link_type = link.get("type", {}).get("name", "").lower()
        inward = link.get("inwardIssue")
        outward = link.get("outwardIssue")

        linked_issue = inward if inward and inward.get("fields", {}).get("issuetype", {}).get("name") == "Task" else \
                       outward if outward and outward.get("fields", {}).get("issuetype", {}).get("name") == "Task" else None

        if linked_issue:
            issue_key = linked_issue["key"]
            issue_summary = linked_issue["fields"]["summary"]

            # Fetch linked task details (again to get full subtask info)
            task_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
            task_data = safe_request("GET", task_url, headers, auth)

            subtasks_raw = task_data.get("fields", {}).get("subtasks", [])
            subtasks = [
                {
                    "id": sub["id"],
                    "key": sub["key"],
                    "summary": sub["fields"]["summary"]
                } for sub in subtasks_raw
            ]

            task_info = {
                "id": task_data["id"],
                "key": issue_key,
                "summary": issue_summary,
                "subtasks": subtasks
            }

            tasks.append(task_info)

    print(f"[DEBUG] Final tasks list for {story_key}: {tasks}")
    return tasks

@app.get("/teams/project", summary="Get users in a project")
def get_users_in_project(project_key: str = Query(..., description="Project key to fetch users for")):
    auth, headers = get_jira_session()
    base_url = f"{JIRA_BASE_URL}/rest/api/3/project/{project_key}/role"

    try:
        roles = safe_request("GET", base_url, headers, auth)
        all_users = []
        for role_name, role_url in roles.items():
            role_data = safe_request("GET", role_url, headers, auth)
            actors = role_data.get("actors", [])

            for actor in actors:
                user_info = {
                    "role": role_name,
                    "displayName": actor.get("displayName"),
                    "accountId": actor.get("actorUser", {}).get("accountId"),
                    "email": actor.get("actorUser", {}).get("emailAddress")
                }
                all_users.append(user_info)

        if not all_users:
            raise HTTPException(status_code=404, detail=f"No users found for project '{project_key}'.")

        return all_users

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users for project: {str(e)}")

@app.get("/hierarchy", response_model=List[BoardModel], summary="Fetch full board-epic-story-task hierarchy")
def build_hierarchical_structure():
    auth, headers = get_jira_session()
    boards_data = []

    for board in fetch_boards():
        epics_data = []
        try:
            epics = fetch_epics(board["id"])
        except Exception as e:
            print(f"[WARN] Failed to fetch epics for board {board['id']}: {e}")
            continue

        for epic in epics:
            stories_data = []
            try:
                stories = fetch_stories(epic["key"])
                for story in stories:
                    tasks = fetch_tasks_and_subtasks(story["key"])
                    task_models = [
                        TaskModel(id=task["id"], key=task["key"], summary=task["fields"]["summary"])
                        for task in tasks
                    ]
                    stories_data.append(
                        StoryModel(
                            id=story["id"],
                            key=story["key"],
                            summary=story["fields"]["summary"],
                            tasks=task_models
                        )
                    )
            except Exception as e:
                print(f"[WARN] Failed to fetch stories/tasks for epic {epic['key']}: {e}")
                continue

            epics_data.append(
                EpicModel(
                    id=str(epic["id"]),
                    name=epic.get("name") or epic.get("summary", "Unnamed Epic"),
                    stories=stories_data
                )
            )

        boards_data.append(
            BoardModel(
                id=board["id"],
                name=board["name"],
                epics=epics_data
            )
        )

    return boards_data

@app.get("/hierarchy/save", summary="Save hierarchy to a file")
def save_hierarchy_to_file():
    data = build_hierarchical_structure()
    file_path = "jira_hierarchy.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([d.dict() for d in data], f, indent=2, ensure_ascii=False)
    return {"status": "success", "message": f"Data saved to {file_path}"}

# ---------------------- CRUD FOR ISSUES ----------------------

@app.post("/issues", summary="Create an issue")
def create_issue(project_key: str, summary: str, issue_type: str = "Task"):
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }
    }
    return safe_request("POST", url, headers, auth, json=payload)

@app.get("/issues", summary="Get all issues in a project")
def list_issues(project_key: str = Query(..., description="Project key like 'KAN'")):
    jql = f"project = {project_key} ORDER BY created DESC"
    return search_issues(jql)

@app.put("/issues/{issue_id}", summary="Update an issue")
def update_issue(issue_id: str, summary: str):
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_id}"
    payload = {"fields": {"summary": summary}}
    return safe_request("PUT", url, headers, auth, json=payload)

@app.delete("/issues/{issue_id}", summary="Delete an issue")
def delete_issue(issue_id: str):
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_id}"
    try:
        response = requests.delete(url, headers=headers, auth=auth)
        response.raise_for_status()
        return {"detail": "Issue deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting issue: {str(e)}")

@app.get("/issues/{issue_key}", summary="Get issue details")
def get_issue(issue_key: str):
    auth, headers = get_jira_session()
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    return safe_request("GET", url, headers, auth)
