"""
Authentication Module for Dynamics 365
=====================================

Handles authentication and provides headers for API requests.
"""

import msal
import requests
from typing import Optional, Dict
import config


class DynamicsAuth:
    """Handles authentication to Dynamics 365."""
    
    def __init__(self):
        self.access_token = None
        self.headers = None
        self.app = msal.PublicClientApplication(
            config.CLIENT_ID, 
            authority=f"https://login.microsoftonline.com/{config.TENANT_DOMAIN}"
        )
    
    def authenticate(self) -> bool:
        """
        Authenticates to Dynamics 365 and stores access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        print("🔐 Authenticating to Dynamics 365...")
        
        try:
            result = self.app.acquire_token_by_username_password(
                config.USERNAME, 
                config.PASSWORD, 
                scopes=["https://dynglobal.crm.dynamics.com/.default"]
            )
            
            if "access_token" not in result:
                print(f"❌ Authentication failed: {result.get('error_description', 'Unknown error')}")
                return False
            
            self.access_token = result["access_token"]
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Prefer': 'return=representation'  # Critical for getting email IDs back
            }
            
            print("✅ Authentication successful!")
            return True
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_headers(self) -> Optional[Dict[str, str]]:
        """
        Returns authentication headers for API requests.
        
        Returns:
            Dict containing headers or None if not authenticated
        """
        if not self.headers:
            if not self.authenticate():
                return None
        
        return self.headers
    
    def test_connection(self) -> bool:
        """
        Tests the connection to Dynamics 365.
        
        Returns:
            bool: True if connection works, False otherwise
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
                print(f"✅ Connection test successful. User ID: {user_info.get('UserId', 'Unknown')}")
                return True
            else:
                print(f"❌ Connection test failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False


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