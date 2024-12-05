import requests
import pytest

def test_search():
    search_url = 'http://localhost:8070/api/search'

    # Perform login to get the token
    login_response = requests.post('http://localhost:8070/api/login', json={'username': 'testuser', 'password': 'canareno!'})
    assert login_response.status_code == 200
    token = login_response.json().get('access_token')

    headers = {'Authorization': f'Bearer {token}'}

    # Test search with query
    response = requests.get(search_url, headers=headers, params={'query': 'test'})
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    for result in results:
        assert 'id' in result
        assert 'jurabk' in result
        assert 'link' in result
        assert 'enbez' in result
        assert 'title' in result
        assert 'content' in result

    # Test search without query
    response = requests.get(search_url, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"error": "Query parameter is required"}


# Run the test
pytest.main(["-v", "server_search_test.py"])