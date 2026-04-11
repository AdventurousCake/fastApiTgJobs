import pytest

from src.tests.conftest import client

# ROUTER_PREFIX = ''

urls_for_test = ["/jobs/hrs_all", "/jobs/jobs_all", "/docs"]

@pytest.mark.parametrize("url", urls_for_test)  # indirect=True
async def test_urls(ac, url):
    # await init_fake_data(limit=10)

    response = await ac.get(url)
    assert response.status_code == 200


# @pytest.mark.parametrize("url", urls_for_test)  # indirect=True
# def test_urls_SYNC(url):
#     response = client.get(url)
#     assert response.status_code == 200