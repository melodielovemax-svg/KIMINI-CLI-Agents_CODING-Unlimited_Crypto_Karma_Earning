import json
import datetime
import os

LOG_DIR = os.path.join(os.getcwd(), "logs")

def audit(event):

    os.makedirs(LOG_DIR, exist_ok=True)

    data={
        "time":
        datetime.datetime.utcnow().isoformat(),

        "event":event
    }

    log_path = os.path.join(LOG_DIR, "kimini-audit.log")
    with open(
        log_path,
        "a"
    ) as f:

        f.write(
            json.dumps(data)+"\n"
        )
