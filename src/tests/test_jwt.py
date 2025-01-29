
class TestJWT:
    url = "/auth/jwt/login"

    async def test_jwt(self, ac):

        username_invalid = 'invalid_username_not_exists'
        password_invalid = 'invalid pwd'
        data_invalid = {
            'username': username_invalid,
            'password': password_invalid
        }

        response = await ac.post(self.url, json=data_invalid)
        assert response.status_code == 400

        username = 'admin'
        password = 'admin'
        data = {
            'username': username,
            'password': password
        }

        response = await ac.post(self.url, json=data)
        assert response.status_code == 200
