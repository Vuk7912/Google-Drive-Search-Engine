import os
import sys
import pytest
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Complex mocking of external dependencies to avoid import errors
class MockHttp:
    pass

class MockDiscovery:
    @staticmethod
    def build(*args, **kwargs):
        return MagicMock()

class MockMediaIoBaseDownload:
    pass

class MockMediaFileUpload:
    pass

sys.modules['apiclient'] = MagicMock()
sys.modules['apiclient.http'] = MagicMock()
sys.modules['apiclient.http.MediaIoBaseDownload'] = MockMediaIoBaseDownload
sys.modules['apiclient.http.MediaFileUpload'] = MockMediaFileUpload
sys.modules['textract'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['oauth2client'] = MagicMock()
sys.modules['oauth2client.file'] = MagicMock()
sys.modules['oauth2client.client'] = MagicMock()
sys.modules['httplib2'] = MockHttp
sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MockDiscovery

# Import the function to test
from app import get_credentials

def test_get_credentials_file_not_exists():
    """Test get_credentials() when credentials file does not exist."""
    with patch('oauth2client.file.Storage') as MockStorage:
        mock_storage_instance = MockStorage.return_value
        mock_storage_instance.get.return_value = None
        
        with patch('os.path.join', return_value='.auth/credentials.json'):
            result = get_credentials()
            assert result is False, "Should return False when no credentials exist"

def test_get_credentials_invalid_credentials():
    """Test get_credentials() with invalid credentials."""
    with patch('oauth2client.file.Storage') as MockStorage:
        mock_storage_instance = MockStorage.return_value
        mock_credentials = MagicMock()
        mock_credentials.invalid = True
        mock_storage_instance.get.return_value = mock_credentials
        
        with patch('os.path.join', return_value='.auth/credentials.json'):
            result = get_credentials()
            assert result is False, "Should return False for invalid credentials"

def test_get_credentials_valid_credentials():
    """Test get_credentials() with valid credentials."""
    def debug_print(message):
        """Capture and log print messages for debugging."""
        print(f"DEBUG: {message}")

    class VerboseMock(MagicMock):
        """Mock that allows capturing method calls."""
        def __call__(self, *args, **kwargs):
            debug_print(f"Mock called with args: {args}, kwargs: {kwargs}")
            return super().__call__(*args, **kwargs)

    with patch('builtins.print', side_effect=debug_print):
        with patch('oauth2client.file.Storage') as MockStorage:
            # Use a different strategy for mocking
            mock_storage_instance = VerboseMock()
            
            # Create a mock credentials object with more realistic behavior
            mock_credentials = MagicMock()
            mock_credentials.invalid = False
            mock_credentials.access_token = "test_access_token"
            mock_credentials.client_id = "test_client_id"
            
            # Configure the mocked Storage
            mock_storage_class = MockStorage
            mock_storage_class.return_value = mock_storage_instance
            mock_storage_instance.get.return_value = mock_credentials
            
            with patch('os.path.join', return_value='.auth/credentials.json'):
                result = get_credentials()
                
                # Detailed debug information
                debug_print(f"Result type: {type(result)}")
                debug_print(f"Result value: {result}")
                debug_print(f"Invalid attribute: {getattr(result, 'invalid', 'Not found')}")
                
                assert result is not False, "Should return credentials when valid"
                assert result.invalid is False, "Returned credentials should be valid"
                assert result.access_token == "test_access_token", "Should return correct credentials"

def test_get_credentials_file_permissions():
    """Test get_credentials() handling of file permission issues."""
    with patch('oauth2client.file.Storage') as MockStorage:
        mock_storage_instance = MockStorage.return_value
        mock_storage_instance.get.side_effect = PermissionError("Mock permission error")
        
        with patch('os.path.join', return_value='.auth/credentials.json'):
            result = get_credentials()
            assert result is False, "Should return False on permission error"

def test_get_credentials_corrupt_file():
    """Test get_credentials() with a corrupt credentials file."""
    with patch('oauth2client.file.Storage') as MockStorage:
        mock_storage_instance = MockStorage.return_value
        mock_storage_instance.get.side_effect = json.JSONDecodeError("", doc="", pos=0)
        
        with patch('os.path.join', return_value='.auth/credentials.json'):
            result = get_credentials()
            assert result is False, "Should return False for corrupt credentials file"