import os

try:
    import litellm
except ImportError:
    litellm = None


class Kimi:
    name = "kimi"

    def __init__(self):
        self.api_key = os.getenv("KIMI_API_KEY")
        self.model = os.getenv("KIMI_MODEL", "kimi-flash-6.9")

    def available(self):
        return bool(self.api_key) and litellm is not None

    async def generate(self, prompt):
        if litellm is None:
            raise RuntimeError(
                "litellm is not installed. Install it with: pip install 'melodie-kimini[relay]'"
            )
        if not self.api_key:
            raise RuntimeError(
                "KIMI_API_KEY is not set. Add it to your environment before chatting."
            )
        response = await litellm.acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key,
        )
        return response.choices[0].message.content
