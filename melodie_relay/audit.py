import json
import datetime
import os

def audit(event):

    data={
        "time":
        datetime.datetime.utcnow().isoformat(),

        "event":event
    }

    log_path = os.path.join("logs", "kimini-audit.log")
    with open(
        log_path,
        "a"
    ) as f:

        f.write(
            json.dumps(data)+"\n"
        )
