"""
Authentication Module for Dynamics 365
=====================================

Handles authentication and provides headers for API requests.
"""

import msal
import requests
from typing import Optional, Dict
import config
from exceptions import (
    DynamicsAuthenticationException, 
    DynamicsConnectionException,
    MissingConfigurationException,
    handle_exception,
    log_exception
)
import logging

logger = logging.getLogger(__name__)


class DynamicsAuth:
    """Handles authentication to Dynamics 365."""
    
    def __init__(self):
        self.access_token = None
        self.headers = None
        self._validate_config()
        
        try:
            self.app = msal.PublicClientApplication(
                config.CLIENT_ID, 
                authority=f"https://login.microsoftonline.com/{config.TENANT_DOMAIN}"
            )
        except Exception as e:
            raise DynamicsAuthenticationException(config.USERNAME, f"Failed to initialize MSAL client: {str(e)}")
    
    def _validate_config(self):
        """Validate required configuration values."""
        if not config.USERNAME:
            raise MissingConfigurationException("USERNAME", "authentication")
        if not config.CLIENT_ID:
            raise MissingConfigurationException("CLIENT_ID", "authentication")
        if not config.TENANT_DOMAIN:
            raise MissingConfigurationException("TENANT_DOMAIN", "authentication")
        
        # Check for password from secure storage
        password = config.get_secure_password() if hasattr(config, 'get_secure_password') else config.PASSWORD
        if not password:
            raise MissingConfigurationException("PASSWORD", "authentication")
    
    @handle_exception
    def authenticate(self) -> bool:
        """
        Authenticates to Dynamics 365 and stores access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            DynamicsAuthenticationException: If authentication fails
            MissingConfigurationException: If required config is missing
        """
        logger.info("🔐 Authenticating to Dynamics 365...")
        
        try:
            # Get password from secure storage if available
            password = config.get_secure_password() if hasattr(config, 'get_secure_password') else config.PASSWORD
            if not password:
                raise MissingConfigurationException("PASSWORD", "authentication")
            
            result = self.app.acquire_token_by_username_password(
                config.USERNAME, 
                password, 
                scopes=["https://dynglobal.crm.dynamics.com/.default"]
            )
            
            if "access_token" not in result:
                error_desc = result.get('error_description', 'Unknown authentication error')
                error_code = result.get('error', 'auth_failed')
                
                # Handle specific error types
                if 'invalid_grant' in error_code.lower() or 'invalid credentials' in error_desc.lower():
                    raise DynamicsAuthenticationException(config.USERNAME, "Invalid username or password")
                elif 'tenant' in error_desc.lower():
                    raise DynamicsAuthenticationException(config.USERNAME, f"Tenant configuration error: {error_desc}")
                elif 'mfa' in error_desc.lower() or 'conditional access' in error_desc.lower():
                    raise DynamicsAuthenticationException(config.USERNAME, "Multi-factor authentication required. Please use interactive authentication.")
                else:
                    raise DynamicsAuthenticationException(config.USERNAME, error_desc)
            
            self.access_token = result["access_token"]
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Prefer': 'return=representation'  # Critical for getting email IDs back
            }
            
            logger.info("✅ Authentication successful!")
            return True
            
        except DynamicsAuthenticationException:
            raise  # Re-raise our custom exceptions
        except MissingConfigurationException:
            raise
        except requests.exceptions.ConnectionError as e:
            raise DynamicsConnectionException("https://login.microsoftonline.com", str(e))
        except Exception as e:
            raise DynamicsAuthenticationException(config.USERNAME, f"Unexpected authentication error: {str(e)}")
    
    def get_headers(self) -> Optional[Dict[str, str]]:
        """
        Returns authentication headers for API requests.
        
        Returns:
            Dict containing headers or None if not authenticated
            
        Raises:
            DynamicsAuthenticationException: If authentication fails
        """
        if not self.headers:
            if not self.authenticate():
                return None
        
        return self.headers
    
    @handle_exception
    def test_connection(self) -> bool:
        """
        Tests the connection to Dynamics 365.
        
        Returns:
            bool: True if connection works, False otherwise
            
        Raises:
            DynamicsConnectionException: If connection fails
            DynamicsAuthenticationException: If authentication fails
        """
        headers = self.get_headers()
        if not headers:
            return False
        
        try:
            response = requests.get(
                f"{config.CRM_BASE_URL}/WhoAmI",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ Connection test successful. User ID: {user_info.get('UserId', 'Unknown')}")
                return True
            elif response.status_code == 401:
                raise DynamicsAuthenticationException(config.USERNAME, "Authentication token expired or invalid")
            elif response.status_code == 403:
                raise DynamicsAuthenticationException(config.USERNAME, "Access denied. Check user permissions.")
            else:
                raise DynamicsConnectionException(config.CRM_BASE_URL, f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError as e:
            raise DynamicsConnectionException(config.CRM_BASE_URL, f"Network connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise DynamicsConnectionException(config.CRM_BASE_URL, f"Connection timeout: {str(e)}")
        except DynamicsAuthenticationException:
            raise  # Re-raise auth exceptions
        except DynamicsConnectionException:
            raise  # Re-raise connection exceptions
        except Exception as e:
            raise DynamicsConnectionException(config.CRM_BASE_URL, f"Unexpected connection error: {str(e)}")


# Global authentication instance
_auth_instance = None

def get_auth() -> DynamicsAuth:
    """Returns the global authentication instance."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = DynamicsAuth()
    return _auth_instance

def get_headers() -> Optional[Dict[str, str]]:
    """Convenience function to get authentication headers."""
    auth = get_auth()
    return auth.get_headers()

@handle_exception
def get_access_token(username: str, password: str) -> Optional[str]:
    """
    Get access token for the given credentials.
    
    Args:
        username: Dynamics 365 username
        password: Dynamics 365 password
        
    Returns:
        Access token string or None if authentication fails
        
    Raises:
        DynamicsAuthenticationException: If authentication fails
    """
    try:
        app = msal.PublicClientApplication(
            config.CLIENT_ID, 
            authority=f"https://login.microsoftonline.com/{config.TENANT_DOMAIN}"
        )
        
        result = app.acquire_token_by_username_password(
            username, 
            password, 
            scopes=["https://dynglobal.crm.dynamics.com/.default"]
        )
        
        if "access_token" not in result:
            error_desc = result.get('error_description', 'Unknown authentication error')
            raise DynamicsAuthenticationException(username, error_desc)
        
        return result["access_token"]
        
    except DynamicsAuthenticationException:
        raise
    except Exception as e:
        raise DynamicsAuthenticationException(username, f"Failed to acquire token: {str(e)}") 