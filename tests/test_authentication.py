import os
import sys
import pytest
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external dependencies
sys.modules['textract'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['oauth2client'] = MagicMock()
sys.modules['oauth2client.file'] = MagicMock()
sys.modules['oauth2client.client'] = MagicMock()
sys.modules['apiclient'] = MagicMock()
sys.modules['httplib2'] = MagicMock()

# Import the function to test
from app import get_credentials

class MockCredentials:
    def __init__(self, invalid=False):
        self.invalid = invalid
        self.access_token = "test_token"
        self.client_id = "test_client_id"

def test_get_credentials_file_not_exists():
    """Test get_credentials() when credentials file does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch the .auth path to use a temp directory
        with patch('os.path.join', return_value=os.path.join(tmpdir, 'credentials.json')):
            # Patch Storage to return None
            with patch('oauth2client.file.Storage.get', return_value=None):
                result = get_credentials()
                assert result is False, "Should return False when no credentials exist"

def test_get_credentials_invalid_credentials():
    """Test get_credentials() with invalid credentials."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock credentials file
        cred_path = os.path.join(tmpdir, 'credentials.json')
        
        # Create a mock Storage that returns invalid credentials
        mock_credentials = MockCredentials(invalid=True)
        
        with patch('os.path.join', return_value=cred_path):
            with patch('oauth2client.file.Storage.get', return_value=mock_credentials):
                result = get_credentials()
                assert result is False, "Should return False for invalid credentials"

def test_get_credentials_valid_credentials():
    """Test get_credentials() with valid credentials."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock credentials file
        cred_path = os.path.join(tmpdir, 'credentials.json')
        
        # Create a mock Storage that returns valid credentials
        mock_credentials = MockCredentials(invalid=False)
        
        with patch('os.path.join', return_value=cred_path):
            with patch('oauth2client.file.Storage.get', return_value=mock_credentials):
                result = get_credentials()
                assert result is not False, "Should return credentials when valid"
                assert result.invalid is False, "Returned credentials should be valid"
                assert result.access_token == "test_token", "Should return correct credentials"

def test_get_credentials_file_permissions():
    """Test get_credentials() handling of file permission issues."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock credentials file with restricted permissions
        cred_path = os.path.join(tmpdir, 'credentials.json')
        
        with patch('os.path.join', return_value=cred_path):
            with patch('oauth2client.file.Storage.get', side_effect=PermissionError):
                with pytest.raises(Exception):
                    get_credentials()

def test_get_credentials_corrupt_file():
    """Test get_credentials() with a corrupt credentials file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock corrupt credentials file
        cred_path = os.path.join(tmpdir, 'credentials.json')
        
        with patch('os.path.join', return_value=cred_path):
            with patch('oauth2client.file.Storage.get', side_effect=json.JSONDecodeError("", doc="", pos=0)):
                result = get_credentials()
                assert result is False, "Should return False for corrupt credentials file"