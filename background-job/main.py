import uuid

from fastapi import FastAPI, HTTPException, Response
from inngest.fast_api import serve
from pydantic import BaseModel

from inngest_client import inngest_client
from functions import say_hello_fn, make_report_fn, heartbeat_fn
from store import reports

app = FastAPI(title="FlyRank Background Job API", version="1.0.0")

serve(app, inngest_client, [say_hello_fn, make_report_fn, heartbeat_fn])


class ReportRequest(BaseModel):
    topic: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=202)
async def create_report(body: ReportRequest):
    if not body.topic or not body.topic.strip():
        raise HTTPException(status_code=400, detail={"error": "topic is required"})

    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "id": report_id,
        "topic": body.topic,
        "status": "pending",
        "result": None,
    }

    await inngest_client.send(
        inngest_client.build_event(
            name="report/requested",
            data={"id": report_id, "topic": body.topic},
        )
    )

    return {"id": report_id, "status": "pending"}


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail={"error": "Report not found"})
    return report


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
