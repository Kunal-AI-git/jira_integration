## JIRA Issue Explorer - FastAPI Service

This FastAPI-based service allows users to interact with their Jira Cloud instance to retrieve and visualize issue data (Epics, Tasks, Stories, Sub-tasks) including nested child relationships, comments, attachments, and metadata.

---

## Features

* Retrieve all Jira boards
* Get projects associated with a board
* Fetch issue hierarchy (Epic -> Tasks/Stories -> Sub-tasks)
* Extract full description, comments, and attachments
* Recursive parsing of child issues
* ADF (Atlassian Document Format) to plain text conversion

---

## Project Structure

```
├── main.py                # FastAPI app with all endpoints and logic
├── .env                   # Stores Jira credentials (not to be committed)
├── requirements.txt       # Python dependencies
```

---

## .env Configuration

You need to set the following environment variables in a `.env` file:

```
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

You can generate a Jira API token from: [https://id.atlassian.com/manage/api-tokens](https://id.atlassian.com/manage/api-tokens)

---

## Run the App

```bash
uvicorn main:app --reload
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.

---

## API Endpoints

### 1. Get Boards

```http
GET /jira/boards
```

Returns list of Jira boards with ID, name, and type.

### 2. Get Projects for a Board

```http
GET /jira/project/{board_id}
```

Returns the projects under a specified board.

### 3. Get Issues by Project Key or Epic Key

```http
GET /jira/issues?key={project_or_epic_key}
```

* If `key=APC`, returns all epics and their nested children in that project.
* If `key=APC-1`, returns details of that epic and its tasks/stories.

**Query param:**

* `key` - Project key (e.g., APC) or Epic key (e.g., APC-1)

---

## Output Format

You’ll receive a list of `IssueDetails` with:

* `id`: Issue Key
* `type`: Epic/Task/Story
* `summary`: Short title
* `description`: Parsed description from ADF
* `comments`: List of comments (author, body, created date)
* `attachments`: List of file attachments with URLs
* `metadata`: Status, priority, assignee, reporter, created/updated timestamps, labels
* `children`: Nested issues recursively

### Example Output

```json
[
  {
    "id": "APC-1",
    "type": "Epic",
    "summary": "Integration of data collection with Chatbot",
    "description": "The Epic contains the feature of how to collect the data from the JIRA.",
    "comments": [...],
    "attachments": [...],
    "metadata": {...},
    "children": [
      {
        "id": "APC-4",
        "type": "Task",
        "summary": "Create a Cron job which will run every week",
        "children": []
      },
      ...
    ]
  },
  ...
]
```

---

## How It Works

1. Authenticates with Jira using Basic Auth (email + API token)
2. Uses Jira REST API (`/search`) and Agile API (`/board`) to get data
3. Converts ADF (Atlassian Document Format) into readable text
4. Recursively fetches children of Epics using `"Epic Link"` or `parent` field
5. Constructs and returns a nested JSON response representing issue hierarchy

---

## Dependencies

* `fastapi` – Web framework
* `pydantic` – Data modeling
* `requests` – REST API interaction
* `python-dotenv` – Env config loader

Install them with:

```bash
pip install -r requirements.txt
```

---

## Notes

* Ensure your Jira user has permission to view issues and comments.
* Keep your API token safe; never expose `.env` in version control.

---

## License

This project is licensed under the MIT License.

---