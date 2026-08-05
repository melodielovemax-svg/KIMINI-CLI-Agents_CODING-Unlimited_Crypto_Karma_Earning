import asyncio
import pytest
from melodie_relay.providers.kimi import Kimi
from melodie_relay.quota import TokenGovernor


def test_kimi_provider_name():
    provider = Kimi()
    assert provider.name == "kimi"


def test_kimi_default_model_is_valid_catalog_id():
    from melodie_kimini.models_catalog import get_model_info
    provider = Kimi()
    assert get_model_info(provider.model) is not None


def test_kimi_generate_requires_configuration():
    import os
    if os.getenv("KIMI_API_KEY"):
        pytest.skip("KIMI_API_KEY is set; live call not tested here")
    provider = Kimi()
    with pytest.raises(RuntimeError):
        asyncio.run(provider.generate("hello"))


def test_quota_governor():
    governor = TokenGovernor()
    governor.record(100)
    assert governor.remaining() <= 500000 - 100


@pytest.mark.parametrize("model_id", ["kimi-flash-3.1", "kimi-pro-max-6.9", "kimi-reason-6.9"])
def test_catalog_models_exist(model_id):
    from melodie_kimini.models_catalog import get_model_info
    assert get_model_info(model_id) is not None
