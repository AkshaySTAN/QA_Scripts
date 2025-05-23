
import pytest
import requests
import json
from unittest.mock import patch, MagicMock

from clubs import create_club, generate_admin_token
from urls import SUPER_URL, ADMIN_URL, BASIC_ENDPOINTS

@pytest.fixture
def mock_requests():
    with patch('clubs.requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mock_generate_admin_token():
    with patch('clubs.generate_admin_token') as mock_token:
        mock_token.return_value = 'mocked_admin_token'
        yield mock_token

@pytest.fixture
def mock_time():
    with patch('clubs.time.sleep') as mock_sleep:
        yield mock_sleep

@pytest.fixture
def mock_last_id():
    with patch('clubs.Last_id', 1000):
        yield

def test_create_club(mock_requests, mock_generate_admin_token, mock_time, mock_last_id):
    # Mock user_ids and token_storage
    user_ids = [1001, 1002, 1003]
    token_storage = ['token1', 'token2', 'token3']

    # Mock generate_admin_token
    mock_generate_admin_token.return_value = 'admin_token'

    # Mock requests.post for assign_mod_category
    mock_assign_mod = MagicMock()
    mock_assign_mod.text = 'Assigned MUGC category'
    
    # Mock requests.post for create_a_club
    mock_create_club = MagicMock()
    mock_create_club.text = 'Club created successfully'
    
    mock_requests.side_effect = [mock_assign_mod, mock_create_club] * len(user_ids)

    # Call the function
    with patch('clubs.user_ids', user_ids), patch('clubs.token_storage', token_storage):
        create_club()

    # Assertions
    assert mock_generate_admin_token.call_count == 1
    assert mock_requests.call_count == 2 * len(user_ids)
    assert mock_time.call_count == len(user_ids)

    for i, user_id in enumerate(user_ids):
        # Check assign_mod_category call
        assign_call = mock_requests.call_args_list[i * 2]
        assert assign_call[1]['json']['id'] == user_id
        assert 'Bearer admin_token' in assign_call[1]['headers']['Authorization']

        # Check create_a_club call
        create_call = mock_requests.call_args_list[i * 2 + 1]
        assert f'{i}_Ludo' in create_call[1]['data']['title']
        assert f'Bearer {token_storage[i]}' in create_call[1]['headers']['Authorization']

    print("All clubs created successfully for each user")