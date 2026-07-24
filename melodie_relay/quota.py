import os


class TokenGovernor:

    def __init__(self):
        self.used=0


    def record(self,tokens):
        self.used += tokens


    def remaining(self):
        limit=int(
            os.getenv(
                "MAX_DAILY_TOKENS",
                "500000"
            )
        )

        return limit-self.used
