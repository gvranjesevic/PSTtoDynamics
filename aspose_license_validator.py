"""
Aspose.Email License Validator
=============================

Validates Aspose.Email license at runtime to prevent unlicensed production use.
"""

import logging
import os
from typing import Optional, Tuple
import warnings

logger = logging.getLogger(__name__)


class AsposeEmailLicenseValidator:
    """Validates Aspose.Email license and provides license management."""
    
    def __init__(self):
        self._license_checked = False
        self._license_valid = False
        self._license_info = None
    
    def validate_license(self, license_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate Aspose.Email license.
        
        Args:
            license_path: Optional path to license file
            
        Returns:
            Tuple of (is_valid, message)
        """
        if self._license_checked:
            return self._license_valid, self._license_info or "License already checked"
        
        try:
            # Try to import Aspose.Email
            import aspose.email as ae
            
            # Check if license file exists
            license_file = license_path or self._find_license_file()
            
            if license_file and os.path.exists(license_file):
                try:
                    # Apply license
                    license_obj = ae.License()
                    license_obj.set_license(license_file)
                    
                    self._license_valid = True
                    self._license_info = f"Valid license applied from {license_file}"
                    logger.info(f"✅ Aspose.Email license validated: {license_file}")
                    
                except Exception as e:
                    self._license_valid = False
                    self._license_info = f"Invalid license file: {e}"
                    logger.error(f"❌ Invalid Aspose.Email license: {e}")
            else:
                # No license file found - check if we're in evaluation mode
                try:
                    # Try to create a simple object to test evaluation mode
                    msg = ae.MailMessage()
                    msg.subject = "Test"
                    
                    # If we get here without exception, we're in evaluation mode
                    self._license_valid = False
                    self._license_info = "Running in evaluation mode - license required for production"
                    logger.warning("⚠️ Aspose.Email running in evaluation mode")
                    
                except Exception as e:
                    self._license_valid = False
                    self._license_info = f"Aspose.Email error: {e}"
                    logger.error(f"❌ Aspose.Email initialization failed: {e}")
            
        except ImportError as e:
            self._license_valid = False
            self._license_info = f"Aspose.Email not installed: {e}"
            logger.error(f"❌ Aspose.Email import failed: {e}")
        
        self._license_checked = True
        return self._license_valid, self._license_info
    
    def _find_license_file(self) -> Optional[str]:
        """
        Find Aspose.Email license file in common locations.
        
        Returns:
            Path to license file if found, None otherwise
        """
        possible_paths = [
            "Aspose.Email.lic",
            "aspose.email.lic", 
            "license/Aspose.Email.lic",
            "licenses/Aspose.Email.lic",
            os.path.expanduser("~/Aspose.Email.lic"),
            os.path.join(os.path.dirname(__file__), "Aspose.Email.lic"),
        ]
        
        # Check environment variable
        env_license = os.getenv("ASPOSE_EMAIL_LICENSE_PATH")
        if env_license:
            possible_paths.insert(0, env_license)
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"Found license file: {path}")
                return path
        
        logger.debug("No license file found in standard locations")
        return None
    
    def require_valid_license(self, allow_evaluation: bool = False) -> None:
        """
        Require a valid license, raising an exception if not found.
        
        Args:
            allow_evaluation: Whether to allow evaluation mode
            
        Raises:
            RuntimeError: If license is invalid and evaluation not allowed
        """
        is_valid, message = self.validate_license()
        
        if not is_valid:
            if allow_evaluation and "evaluation mode" in message.lower():
                warnings.warn(
                    "Running Aspose.Email in evaluation mode. "
                    "A valid license is required for production use.",
                    UserWarning,
                    stacklevel=2
                )
                logger.warning("⚠️ Continuing with evaluation mode license")
                return
            
            error_msg = (
                f"Aspose.Email license validation failed: {message}\n\n"
                "For production use, you need a valid Aspose.Email license.\n"
                "Please:\n"
                "1. Obtain a license from https://products.aspose.com/email/python-net/\n"
                "2. Place the license file as 'Aspose.Email.lic' in the project root\n"
                "3. Or set ASPOSE_EMAIL_LICENSE_PATH environment variable\n"
                "4. Or pass the license path to validate_license()\n\n"
                "For development/testing, you can use evaluation mode by setting "
                "allow_evaluation=True"
            )
            
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def get_license_status(self) -> dict:
        """
        Get detailed license status information.
        
        Returns:
            Dictionary with license status details
        """
        if not self._license_checked:
            self.validate_license()
        
        return {
            "valid": self._license_valid,
            "message": self._license_info,
            "checked": self._license_checked,
            "evaluation_mode": self._license_info and "evaluation mode" in self._license_info.lower()
        }


# Global validator instance
_license_validator = AsposeEmailLicenseValidator()


def validate_aspose_license(license_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate Aspose.Email license (convenience function).
    
    Args:
        license_path: Optional path to license file
        
    Returns:
        Tuple of (is_valid, message)
    """
    return _license_validator.validate_license(license_path)


def require_aspose_license(allow_evaluation: bool = False) -> None:
    """
    Require a valid Aspose.Email license (convenience function).
    
    Args:
        allow_evaluation: Whether to allow evaluation mode
        
    Raises:
        RuntimeError: If license is invalid and evaluation not allowed
    """
    _license_validator.require_valid_license(allow_evaluation)


def get_aspose_license_status() -> dict:
    """
    Get Aspose.Email license status (convenience function).
    
    Returns:
        Dictionary with license status details
    """
    return _license_validator.get_license_status()


if __name__ == "__main__":
    # Test license validation
    print("Testing Aspose.Email license validation...")
    
    validator = AsposeEmailLicenseValidator()
    is_valid, message = validator.validate_license()
    
    print(f"License valid: {is_valid}")
    print(f"Message: {message}")
    
    status = validator.get_license_status()
    print(f"Status: {status}")
    
    # Test requirement (with evaluation allowed for testing)
    try:
        validator.require_valid_license(allow_evaluation=True)
        print("✅ License requirement passed")
    except RuntimeError as e:
        print(f"❌ License requirement failed: {e}") 