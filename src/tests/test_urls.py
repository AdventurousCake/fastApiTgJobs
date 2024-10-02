import pytest

# from fastapi.testclient import TestClient as test_client


class TestNewpage:
    def test_newpage(test_client):
        response = test_client.get('/newpage')
        assert response.status_code == 200


@pytest.mark.parametrize(
    "url",
    [
        # "/jobs",
        "/jobs/hrs_all",
        "/jobs/jobs_all",
        "/docs",
        # "/newpage",
        # "/404",
    ],
    # indirect=True
)
async def test_urls(ac, url):
    # await init_fake_data(limit=10)

    response = await ac.get(url)
    assert response.status_code == 200


# def test_urls(test_client, url):
#     response = test_client.get(url)
#     assert response.status_code == 200
