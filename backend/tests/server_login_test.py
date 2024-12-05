import pytest
import requests

def test_login():
    url = 'http://localhost:8070/api/login'

    # Test successful login
    response = requests.post(url, json={'username': 'testuser', 'password': 'canareno!'})
    assert response.status_code == 200
    assert 'access_token' in response.json()

    # Test login with bad password
    response = requests.post(url, json={'username': 'testuser', 'password': 'bad_password'})
    assert response.status_code == 401
    assert response.json() == {"msg": "Bad username or password"}

    # Test login with non-existent user
    response = requests.post(url, json={'username': 'non_existent_user', 'password': 'test_password'})
    assert response.status_code == 401
    assert response.json() == {"msg": "Bad username or password"}

# Run the test
pytest.main(["-v", "server_login_test.py"])