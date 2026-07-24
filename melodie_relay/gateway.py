from melodie_relay.providers.kimi import Kimi
from melodie_relay.scheduler import throttle
from melodie_relay.audit import audit


providers=[
    Kimi()
]


async def run(prompt):

    await throttle()


    for provider in providers:

        try:

            result=await provider.generate(prompt)

            audit(
                "SUCCESS:"+provider.name
            )

            return result


        except Exception as e:

            audit(
                "FAILED:"+str(e)
            )


    raise Exception(
        "No providers available"
    )
