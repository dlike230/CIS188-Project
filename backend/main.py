import base64
from typing import List

from fastapi import FastAPI
import requests
import json
import yaml
import base64

from pydantic import BaseModel
from starlette.responses import Response

app = FastAPI()

EVENTS_URL = "https://api.github.com/repos/VishaalPKumar/CIS188-Project/contents/data/events.yaml"
TOKEN = "***REMOVED***"


def get_metadata():
    metadata_response = requests.get(
        EVENTS_URL,
        headers={"Authorization": f"token {TOKEN}"}
    ).content

    return json.loads(metadata_response)


@app.get("/events")
def get_events():
    metadata = get_metadata()
    download_url = metadata["download_url"]

    return yaml.safe_load(requests.get(download_url).content)


class Event(BaseModel):
    date: str
    time: str
    description: str
    name: str


class Events(BaseModel):
    events: List[Event]


@app.post("/updateEvents")
def update_events(events: Events):
    new_data = events.dict()
    new_yaml = yaml.safe_dump(new_data)
    metadata = get_metadata()

    data = {
        "message": "Update events",
        "sha": metadata["sha"],
        "branch": "master",
        "committer": {
            "name": "Daniel Like",
            "email": "dlike230@gmail.com"
        },
        "content": base64.b64encode(str.encode(new_yaml)).decode()
    }

    res = requests.put(
        EVENTS_URL,
        data=json.dumps(data),
        headers={
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/json"
        },
    )

    return Response(content=res.content, status_code=res.status_code)
