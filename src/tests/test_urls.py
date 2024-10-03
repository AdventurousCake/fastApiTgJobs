import pytest

# from fastapi.testclient import TestClient as test_client


# class TestNewpage:
#     def test_newpage(ac):
#         response = ac.get('/newpage')
#         assert response.status_code == 200

values_for_test = ["/jobs/hrs_all", "/jobs/jobs_all", "/docs"]
@pytest.mark.parametrize("url", values_for_test)  # indirect=True
async def test_urls(ac, url):
    # await init_fake_data(limit=10)

    response = await ac.get(url)
    assert response.status_code == 200


# def test_urls(test_client, url):
#     response = test_client.get(url)
#     assert response.status_code == 200
