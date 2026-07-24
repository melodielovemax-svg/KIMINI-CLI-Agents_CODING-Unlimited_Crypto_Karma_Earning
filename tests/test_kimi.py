import pytest
from melodie_relay.providers.kimi import Kimi

@pytest.mark.asyncio
async def test_kimi_provider():
    provider = Kimi()
    assert provider.name == "kimi"
    # This test would require a mocked Kimi API or env vars
    # assert await provider.generate("hello") is not None
