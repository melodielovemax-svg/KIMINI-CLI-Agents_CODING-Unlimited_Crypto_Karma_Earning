from melodie_relay.providers.kimi import Kimi
from melodie_relay.scheduler import throttle
from melodie_relay.audit import audit
from melodie_relay.quota import TokenGovernor


providers = [
    Kimi()
]

governor = TokenGovernor()


async def run(prompt):

    await throttle()

    for provider in providers:
        if not provider.available():
            audit("SKIPPED:" + provider.name)
            continue
        try:
            result = await provider.generate(prompt)
            governor.record(len(result or ""))
            audit("SUCCESS:" + provider.name)
            return result
        except Exception as e:
            audit("FAILED:" + str(e))

    raise Exception("No providers available")
