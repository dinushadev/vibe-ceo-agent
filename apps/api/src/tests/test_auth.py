import pytest
from unittest.mock import patch, MagicMock
from src.services.google_auth_service import GoogleAuthService

@pytest.mark.asyncio
async def test_verify_google_token_success():
    """Test successful token verification"""
    service = GoogleAuthService()
    
    # Mock data
    mock_id_info = {
        'sub': '123456789',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'http://example.com/pic.jpg'
    }
    
    # Patch id_token.verify_oauth2_token
    with patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
        mock_verify.return_value = mock_id_info
        
        result = await service.verify_google_token("valid_token")
        
        assert result is not None
        assert result['google_id'] == '123456789'
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

@pytest.mark.asyncio
async def test_verify_google_token_invalid():
    """Test invalid token verification"""
    service = GoogleAuthService()
    
    # Patch id_token.verify_oauth2_token to raise ValueError
    with patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
        mock_verify.side_effect = ValueError("Invalid token")
        
        result = await service.verify_google_token("invalid_token")
        
        assert result is None
