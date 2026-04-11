import logging


async def test_register_already_exists(ac):
    response = await ac.post('/auth/register',
                             json={"email": "admin_pytest@test.com", "username": "admin_pytest" , "password": "admin"})
    assert response.status_code == 400
    assert response.json() == {'detail': 'REGISTER_USER_ALREADY_EXISTS'}


async def test_register(ac):
    response = await ac.post('/auth/register',
                             json={"email": "user123@user.com", "username": "user123" , "password": "user123"})
    logging.debug(f"{response.json()=}\n{response.status_code=}")

    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"req: {response.request}")


    assert response.status_code == 201

    data = response.json()
    data.pop("id")
    assert data == {
        "email": "user123@user.com",
        "username": "user123",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }

    # response = await ac.post('/auth/jwt/login',
    #                          data={"username": "user123", "password": "user123"})

    # assert response.status_code == 200
    # assert "access_token" in response.json()