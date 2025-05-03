from fastapi import FastAPI, Query, HTTPException
from typing import List, Dict
import requests
import os
from dotenv import load_dotenv
import base64
from pydantic import BaseModel
import re

# Load .env variables
load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise Exception("Missing one or more environment variables.")

# Base64 encode auth string
auth_str = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
encoded_auth = base64.b64encode(auth_str.encode()).decode()

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Basic {encoded_auth}"
}

JIRA_API_URL = f"https://{JIRA_DOMAIN}/rest/agile/1.0"
JIRA_REST_API_URL = f"https://{JIRA_DOMAIN}/rest/api/3"

app = FastAPI()

ISSUE_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


# ---------- MODELS ----------

class Comment(BaseModel):
    author: str
    body: str
    created: str

class Attachment(BaseModel):
    filename: str
    url: str
    mimeType: str

class Metadata(BaseModel):
    status: str
    priority: str
    assignee: str
    reporter: str
    created: str
    updated: str
    labels: List[str]

class IssueDetails(BaseModel):
    id: str
    type: str
    summary: str
    description: str
    comments: List[Comment]
    attachments: List[Attachment]
    metadata: Metadata
    children: List['IssueDetails'] = []  # Recursive nesting

IssueDetails.update_forward_refs()

# ---------- HELPERS ----------

def extract_adf_text(adf_node):
    if isinstance(adf_node, dict):
        text = adf_node.get("text", "")
        content = adf_node.get("content", [])
        return text + " " + " ".join(extract_adf_text(child) for child in content)
    elif isinstance(adf_node, list):
        return " ".join(extract_adf_text(item) for item in adf_node)
    return ""

def get_issues_jql(jql: str) -> List[Dict]:
    url = f"{JIRA_REST_API_URL}/search"
    params = {
        "jql": jql,
        "maxResults": 50,
        "fields": "summary,description,comment,attachment,issuetype,status,priority,assignee,reporter,created,updated,labels"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json().get("issues", [])


def parse_issue(issue: Dict) -> IssueDetails:
    fields = issue["fields"]

    # Parse description from ADF
    adf_description = fields.get("description", {})
    description = extract_adf_text(adf_description.get("content", [])) if adf_description else ""

    # Parse comments
    comments = [
        Comment(
            author=c["author"]["displayName"],
            body=extract_adf_text(c["body"].get("content", [])) if "body" in c else "",
            created=c["created"]
        )
        for c in fields.get("comment", {}).get("comments", [])
    ]

    # Parse attachments
    attachments = [
        Attachment(
            filename=a["filename"],
            url=a["content"],
            mimeType=a["mimeType"]
        )
        for a in fields.get("attachment", [])
    ]

    # Parse metadata
    metadata = Metadata(
        status=fields["status"]["name"] if fields.get("status") else "",
        priority=fields["priority"]["name"] if fields.get("priority") else "",
        assignee=fields["assignee"]["displayName"] if fields.get("assignee") else "Unassigned",
        reporter=fields["reporter"]["displayName"] if fields.get("reporter") else "",
        created=fields["created"],
        updated=fields["updated"],
        labels=fields.get("labels", [])
    )

    return IssueDetails(
        id=issue["key"],
        type=fields["issuetype"]["name"] if fields.get("issuetype") else "",
        summary=fields.get("summary", ""),
        description=description.strip(),
        comments=comments,
        attachments=attachments,
        metadata=metadata
    )

def remove_duplicates_recursive(issues: List[Dict]) -> List[Dict]:
    seen_ids = set()

    def deduplicate(issue: Dict) -> Dict:
        if issue['id'] in seen_ids:
            return None  # Duplicate, skip it
        seen_ids.add(issue['id'])
        # Recurse into children
        children = issue.get('children', [])
        unique_children = []
        for child in children:
            result = deduplicate(child)
            if result:
                unique_children.append(result)
        issue['children'] = unique_children
        return issue

    unique_issues = []
    for issue in issues:
        result = deduplicate(issue)
        if result:
            unique_issues.append(result)

    return unique_issues


# ---------- ROUTES ----------

@app.get("/jira/boards")
def get_boards():
    url = f"{JIRA_API_URL}/board"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    boards = response.json().get("values", [])
    return [{"id": b["id"], "name": b["name"], "type": b["type"]} for b in boards]


@app.get("/jira/project/{board_id}")
def get_project_key(board_id: int):
    url = f"{JIRA_API_URL}/board/{board_id}/project"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    projects = response.json().get("values", [])
    return [{"id": p["id"], "key": p["key"], "name": p["name"]} for p in projects]

# Function to get child issues (using both Epic Link and Parent fields)
def get_child_issues(parent_key: str) -> List[Dict]:
    # First, attempt to find issues under "Epic Link" (Stories, Tasks under Epics)
    try:
        epic_issues = get_issues_jql(f'"Epic Link" = {parent_key}')
    except HTTPException as e:
        epic_issues = []  # If Epic Link doesn't exist, we proceed with parent-child relationship
    
    # If no issues are found under "Epic Link", fallback to fetching child issues via "parent" (Sub-Tasks)
    if not epic_issues:
        try:
            epic_issues = get_issues_jql(f'parent = {parent_key}')
        except HTTPException as e:
            epic_issues = []  # If no children under parent field, return empty list
    
    return epic_issues

# Function to parse issues including children (recursively)
def parse_issue_with_children(issue: Dict) -> IssueDetails:
    fields = issue["fields"]
    children = []

    # Parse description from ADF
    adf_description = fields.get("description", {})
    description = extract_adf_text(adf_description.get("content", [])) if adf_description else ""

    # Parse comments
    comments = [
        Comment(
            author=c["author"]["displayName"],
            body=extract_adf_text(c["body"].get("content", [])) if "body" in c else "",
            created=c["created"]
        )
        for c in fields.get("comment", {}).get("comments", [])
    ]

    # Parse attachments
    attachments = [
        Attachment(
            filename=a["filename"],
            url=a["content"],
            mimeType=a["mimeType"]
        )
        for a in fields.get("attachment", [])
    ]

    # Parse metadata
    metadata = Metadata(
        status=fields["status"]["name"] if fields.get("status") else "",
        priority=fields["priority"]["name"] if fields.get("priority") else "",
        assignee=fields["assignee"]["displayName"] if fields.get("assignee") else "Unassigned",
        reporter=fields["reporter"]["displayName"] if fields.get("reporter") else "",
        created=fields["created"],
        updated=fields["updated"],
        labels=fields.get("labels", [])
    )

    # If it's an Epic, recursively fetch child issues (Stories, Tasks, Sub-Tasks)
    if fields["issuetype"]["name"] == "Epic":
        children = get_child_issues(issue["key"])

    return IssueDetails(
        id=issue["key"],
        type=fields["issuetype"]["name"] if fields.get("issuetype") else "",
        summary=fields.get("summary", ""),
        description=description.strip(),
        comments=comments,
        attachments=attachments,
        metadata=metadata,
        # Adding the children as nested issues (sub-tasks, stories, etc.)
        children=[parse_issue_with_children(child) for child in children]
    )

# Endpoint to get issues with child hierarchy
@app.get("/jira/issues", response_model=List[IssueDetails])
def get_jira_issues(key: str = Query(..., description="Project Key or Epic Key")):
    try:
        if ISSUE_KEY_PATTERN.match(key):  # Likely an Epic Key
            epic_issue = get_issues_jql(f'key = {key}')
            if not epic_issue:
                raise HTTPException(status_code=404, detail="Epic not found.")
            parsed_epic = parse_issue_with_children(epic_issue[0])
            return [parsed_epic]
        else:  # Project Key
            epics = get_issues_jql(f'project = "{key}" AND issuetype = Epic ORDER BY created ASC')
            parsed_issues = [parse_issue_with_children(epic) for epic in epics]
            # Children are already nested, so no need to deduplicate externally
            return parsed_issues
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
