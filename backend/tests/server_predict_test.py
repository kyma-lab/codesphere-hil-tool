import pytest
import requests
import time
from validation import validateIOB

def test_prediction_endpoint():
    prediction_url = 'http://localhost:8070/api/getpredictions'

    # Perform login to get the token
    login_response = requests.post('http://localhost:8070/api/login', json={'username': 'testuser', 'password': 'canareno!'})
    assert login_response.status_code == 200
    token = login_response.json().get('access_token')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # Test with no file
    response = requests.post(prediction_url, headers=headers)
    assert response.status_code == 400
    print(response.text)
    assert "Failed to decode JSON" in response.text

    # Test with no authorization
    response = requests.get(prediction_url)
    assert response.status_code == 405

    # Test with single file and time limit
    start_time = time.time()
    with open('res/test.txt', 'rb') as f:
        text = f.readlines()
        text = " ".join([line.decode('utf-8') for line in text])
        payload = {'texts': [text], 'userid': "testuser"}

        response = requests.post(prediction_url, json=payload, headers=headers)
        assert response.status_code == 200

    end_time = time.time()
    execution_time = end_time - start_time
    assert execution_time <= 20

    # Test with two files and time limit
    start_time = time.time()
    with open('res/test.txt', 'rb') as f:
        text = f.readlines()
        text = " ".join([line.decode('utf-8') for line in text])
        payload = {'texts': [text, text], 'userid': "testuser"}

        response = requests.post(prediction_url, json=payload, headers=headers)
        assert response.status_code == 200

    end_time = time.time()
    execution_time = end_time - start_time
    assert execution_time <= 20

    # verify that the response is valid IOB format
    response_json = response.json()
    data = response_json['texts']

    for result in data:
        # accept 1 error, because the model is not perfect, just as you
        assert validateIOB(result, count=True, verbose=True, tab_separated=False) <= 1


pytest.main(["-v", "server_predict_test.py"])