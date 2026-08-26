import datetime

import inngest

from inngest_client import inngest_client
from store import reports


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello_fn(ctx: inngest.Context, step: inngest.Step) -> dict:
    await step.sleep("wait-a-moment", datetime.timedelta(seconds=5))
    return {"message": "Hello from the background!"}


@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report_fn(ctx: inngest.Context, step: inngest.Step) -> dict:
    report_id: str = ctx.event.data["id"]
    topic: str = ctx.event.data["topic"]

    await step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    def build() -> str:
        if topic == "fail":
            raise Exception("The report oven is broken!")
        result = f"Report on {topic} — generated at {datetime.datetime.now()}"
        reports[report_id] = {
            **reports[report_id],
            "status": "done",
            "result": result,
        }
        return result

    result = await step.run("build-report", build)
    return {"result": result}


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat_fn(ctx: inngest.Context, step: inngest.Step) -> dict:
    pending_count = sum(1 for r in reports.values() if r.get("status") == "pending")
    done_count = sum(1 for r in reports.values() if r.get("status") == "done")
    total = len(reports)
    print(f"Heartbeat — pending: {pending_count}, done: {done_count}, total: {total}")
    return {"pending": pending_count, "done": done_count, "total": total}
