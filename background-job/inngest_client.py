import os
import inngest
from dotenv import load_dotenv

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="report-api",
    signing_key=os.getenv("INNGEST_SIGNING_KEY", "local"),
    event_key=os.getenv("INNGEST_EVENT_KEY", "local"),
    is_production=False,
)
