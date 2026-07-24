import os
import litellm

class Kimi:
    name="kimi"

    async def generate(self, prompt):
        # Using litellm for Kimi API
        response = await litellm.acompletion(
            model="kimi-56",
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv("KIMI_API_KEY")
        )
        return response.choices[0].message.content
