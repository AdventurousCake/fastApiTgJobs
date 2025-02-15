import pytest

# ROUTER_PREFIX = ''

# values_for_test = ["/jobs/hrs_all", "/jobs/jobs_all", "/jobs/search", "/docs"]
values_for_test = ["/jobs/hrs_all", "/jobs/jobs_all", "/docs"]
@pytest.mark.parametrize("url", values_for_test)  # indirect=True
async def test_urls(ac, url):
    # await init_fake_data(limit=10)

    response = await ac.get(url)
    assert response.status_code == 200
