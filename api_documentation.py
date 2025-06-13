"""
PST-to-Dynamics 365 API Documentation
=====================================

logger = logging.getLogger(__name__)

This module provides comprehensive API documentation for all core components
of the PST-to-Dynamics 365 email import system.

Author: AI Assistant
Version: 1.0
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import inspect
import logging


class ModuleStatus(Enum):
    """Status of API modules."""
    STABLE = "stable"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


@dataclass
class APIEndpoint:
    """Represents an API endpoint or method."""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: str
    raises: List[str]
    examples: List[str]
    status: ModuleStatus = ModuleStatus.STABLE


@dataclass
class APIModule:
    """Represents an API module."""
    name: str
    description: str
    version: str
    status: ModuleStatus
    endpoints: List[APIEndpoint]
    examples: List[str]


class APIDocumentationGenerator:
    """Generates comprehensive API documentation."""
    
    def __init__(self):
        self.modules: Dict[str, APIModule] = {}
        self._register_core_modules()
    
    def _register_core_modules(self):
        """Register all core API modules."""
        
        # Email Importer Module
        self.modules['email_importer'] = APIModule(
            name="EmailImporter",
            description="""
            Core email import functionality with intelligent processing.
            
            The EmailImporter module provides comprehensive email import capabilities
            including PST file reading, duplicate detection, batch processing, and
            error handling. It serves as the primary interface for importing emails
            from PST files into Dynamics 365 CRM.
            
            Key Features:
            - PST file reading and parsing
            - Intelligent duplicate detection
            - Batch processing with progress tracking
            - Comprehensive error handling and recovery
            - Performance optimization for large datasets
            - Real-time progress monitoring
            """,
            version="2.0",
            status=ModuleStatus.STABLE,
            endpoints=[
                APIEndpoint(
                    name="import_emails",
                    description="""
                    Import emails from a PST file to Dynamics 365 CRM.
                    
                    This method performs a complete email import operation including:
                    - PST file validation and reading
                    - Contact matching and creation
                    - Duplicate detection and prevention
                    - Batch processing for optimal performance
                    - Progress tracking and error reporting
                    """,
                    parameters={
                        "pst_path": "str - Path to the PST file to import",
                        "batch_size": "int - Number of emails to process per batch (default: 50)",
                        "create_contacts": "bool - Whether to automatically create missing contacts (default: True)",
                        "skip_duplicates": "bool - Whether to skip duplicate emails (default: True)",
                        "progress_callback": "callable - Optional callback for progress updates",
                        "conflict_resolution": "str - Strategy for resolving conflicts ('manual', 'auto', 'skip')"
                    },
                    returns="ImportResults - Comprehensive results including success/failure counts, created contacts, and error details",
                    raises=[
                        "PSTFileNotFoundException - If the PST file cannot be found",
                        "PSTFileCorruptedException - If the PST file is corrupted or invalid",
                        "DynamicsAuthenticationException - If authentication to Dynamics 365 fails",
                        "EmailImportException - If specific email import operations fail"
                    ],
                    examples=[
                        """
                        # Basic email import
                        from email_importer import EmailImporter
                        
                        importer = EmailImporter()
                        results = importer.import_emails('path/to/emails.pst')
                        logger.debug("Imported {results.successful_imports} emails")
                        """,
                        """
                        # Advanced import with custom settings
                        importer = EmailImporter()
                        results = importer.import_emails(
                            pst_path='large_mailbox.pst',
                            batch_size=100,
                            create_contacts=True,
                            progress_callback=lambda progress: logger.debug("Progress: {progress}%")
                        )
                        """
                    ]
                ),
                APIEndpoint(
                    name="validate_pst_file",
                    description="Validate a PST file for import readiness",
                    parameters={
                        "pst_path": "str - Path to the PST file to validate"
                    },
                    returns="ValidationResult - Detailed validation results including file integrity, size, and email count",
                    raises=[
                        "PSTFileNotFoundException - If file does not exist",
                        "PSTFileCorruptedException - If file is corrupted"
                    ],
                    examples=[
                        """
                        validation = importer.validate_pst_file('emails.pst')
                        if validation.is_valid:
                            logger.debug("PST file contains {validation.email_count} emails")
                        """
                    ]
                ),
                APIEndpoint(
                    name="get_import_preview",
                    description="Preview what would be imported without actually importing",
                    parameters={
                        "pst_path": "str - Path to the PST file",
                        "sample_size": "int - Number of emails to analyze for preview (default: 100)"
                    },
                    returns="ImportPreview - Preview of contacts, email types, and potential issues",
                    raises=["PSTFileNotFoundException", "PSTReadException"],
                    examples=[
                        """
                        preview = importer.get_import_preview('emails.pst')
                        logger.debug("Will create {len(preview.new_contacts)} new contacts")
                        logger.debug("Found {len(preview.potential_duplicates)} potential duplicates")
                        """
                    ]
                )
            ],
            examples=[
                """
                # Complete email import workflow
                from email_importer import EmailImporter
                from exceptions import PSTDynamicsException
                
                try:
                    importer = EmailImporter()
                    
                    # Validate PST file first
                    validation = importer.validate_pst_file('mailbox.pst')
                    if not validation.is_valid:
                        logger.debug("PST validation failed: {validation.error_message}")
                        return
                    
                    # Get preview of import
                    preview = importer.get_import_preview('mailbox.pst')
                    logger.debug("Preview: {len(preview.emails)} emails, {len(preview.new_contacts)} new contacts")
                    
                    # Perform import with progress tracking
                    def progress_handler(progress_data):
                        logger.debug("Progress: {progress_data.percentage}% - {progress_data.current_operation}")
                    
                    results = importer.import_emails(
                        pst_path='mailbox.pst',
                        batch_size=50,
                        progress_callback=progress_handler
                    )
                    
                    logger.debug("Import completed:")
                    logger.debug("  Successful: {results.successful_imports}")
                    logger.debug("  Failed: {results.failed_imports}")
                    logger.debug("  Contacts created: {results.contacts_created}")
                    
                except PSTDynamicsException as e:
                    logger.debug("Import failed: {e.get_user_friendly_message()}")
                """
            ]
        )
        
        # Sync Engine Module
        self.modules['sync_engine'] = APIModule(
            name="SyncEngine",
            description="""
            Advanced synchronization engine with conflict resolution.
            
            The SyncEngine provides sophisticated bi-directional synchronization
            capabilities between PST files and Dynamics 365 CRM. It includes
            intelligent conflict detection, multiple resolution strategies,
            and comprehensive monitoring.
            """,
            version="2.0",
            status=ModuleStatus.STABLE,
            endpoints=[
                APIEndpoint(
                    name="sync_data",
                    description="Synchronize data between source and target systems",
                    parameters={
                        "source": "DataSource - Source system data provider",
                        "target": "DataSource - Target system data provider",
                        "conflict_strategy": "ConflictResolutionStrategy - How to handle conflicts",
                        "sync_direction": "str - 'bidirectional', 'source_to_target', or 'target_to_source'"
                    },
                    returns="SyncResults - Detailed synchronization results and metrics",
                    raises=[
                        "SyncConflictException - When conflicts cannot be automatically resolved",
                        "SyncValidationException - When data validation fails"
                    ],
                    examples=[
                        """
                        sync_engine = SyncEngine()
                        results = sync_engine.sync_data(
                            source=pst_data_source,
                            target=dynamics_data_source,
                            conflict_strategy=ConflictResolutionStrategy.LAST_WRITE_WINS
                        )
                        """
                    ]
                )
            ],
            examples=[]
        )
        
        # Contact Manager Module
        self.modules['contact_manager'] = APIModule(
            name="ContactManager",
            description="""
            Comprehensive contact management with relationship tracking.
            
            The ContactManager provides advanced contact management capabilities
            including automatic contact creation, relationship mapping, bulk
            operations, and comprehensive search functionality.
            """,
            version="1.5",
            status=ModuleStatus.STABLE,
            endpoints=[
                APIEndpoint(
                    name="create_contact",
                    description="Create a new contact from email data",
                    parameters={
                        "email_data": "EmailData - Email information to extract contact from",
                        "validation_rules": "List[ValidationRule] - Custom validation rules to apply",
                        "merge_duplicates": "bool - Whether to merge with existing similar contacts"
                    },
                    returns="Contact - Created contact object with all extracted information",
                    raises=[
                        "ContactCreationException - When contact creation fails",
                        "DuplicateContactException - When duplicate detection prevents creation"
                    ],
                    examples=[
                        """
                        contact_manager = ContactManager()
                        contact = contact_manager.create_contact(
                            email_data=email_info,
                            merge_duplicates=True
                        )
                        """
                    ]
                )
            ],
            examples=[]
        )
        
        # Authentication Module
        self.modules['auth'] = APIModule(
            name="Authentication",
            description="""
            Secure authentication system for Dynamics 365 integration.
            
            The Authentication module provides comprehensive authentication
            capabilities including OAuth2 flows, token management, MFA support,
            and secure credential storage.
            """,
            version="1.0",
            status=ModuleStatus.STABLE,
            endpoints=[
                APIEndpoint(
                    name="authenticate",
                    description="Authenticate with Dynamics 365 using various methods",
                    parameters={
                        "method": "str - Authentication method ('oauth2', 'client_credentials', 'username_password')",
                        "credentials": "Dict[str, str] - Authentication credentials",
                        "scopes": "List[str] - Required OAuth2 scopes"
                    },
                    returns="AuthenticationResult - Authentication tokens and metadata",
                    raises=[
                        "DynamicsAuthenticationException - When authentication fails",
                        "MissingConfigurationException - When required configuration is missing"
                    ],
                    examples=[
                        """
                        auth = Authentication()
                        result = auth.authenticate(
                            method='oauth2',
                            credentials={'username': 'user@company.com'},
                            scopes=['https://dynglobal.crm.dynamics.com/.default']
                        )
                        """
                    ]
                )
            ],
            examples=[]
        )
        
        # Configuration Module
        self.modules['config'] = APIModule(
            name="Configuration",
            description="""
            Centralized configuration management system.
            
            The Configuration module provides secure, environment-aware
            configuration management with validation, default values,
            and secure credential handling.
            """,
            version="1.0",
            status=ModuleStatus.STABLE,
            endpoints=[
                APIEndpoint(
                    name="get_secure_password",
                    description="Retrieve password from secure storage",
                    parameters={},
                    returns="Optional[str] - Password if available, None otherwise",
                    raises=[],
                    examples=[
                        """
                        import config
                        password = config.get_secure_password()
                        if password:
                            logger.debug("Password retrieved from secure storage")
                        """
                    ]
                ),
                APIEndpoint(
                    name="validate_config",
                    description="Validate current configuration settings",
                    parameters={},
                    returns="List[str] - List of validation errors (empty if valid)",
                    raises=[],
                    examples=[
                        """
                        errors = config.validate_config()
                        if errors:
                            logger.debug("Configuration errors: {errors}")
                        """
                    ]
                )
            ],
            examples=[]
        )
    
    def generate_markdown_docs(self) -> str:
        """Generate comprehensive markdown documentation."""
        
        docs = []
        docs.append("# PST-to-Dynamics 365 API Reference\n")
        docs.append("Comprehensive API documentation for all modules and components.\n")
        
        for module_name, module in self.modules.items():
            docs.append(f"## {module.name} Module\n")
            docs.append(f"**Version:** {module.version}  ")
            docs.append(f"**Status:** {module.status.value.title()}\n")
            docs.append(f"{module.description}\n")
            
            if module.endpoints:
                docs.append("### Methods\n")
                
                for endpoint in module.endpoints:
                    docs.append(f"#### `{endpoint.name}`\n")
                    docs.append(f"{endpoint.description}\n")
                    
                    if endpoint.parameters:
                        docs.append("**Parameters:**\n")
                        for param, desc in endpoint.parameters.items():
                            docs.append(f"- `{param}`: {desc}\n")
                        docs.append("")
                    
                    docs.append(f"**Returns:** {endpoint.returns}\n")
                    
                    if endpoint.raises:
                        docs.append("**Raises:**\n")
                        for exc in endpoint.raises:
                            docs.append(f"- {exc}\n")
                        docs.append("")
                    
                    if endpoint.examples:
                        docs.append("**Examples:**\n")
                        for example in endpoint.examples:
                            docs.append("```python")
                            docs.append(example.strip())
                            docs.append("```\n")
            
            if module.examples:
                docs.append("### Complete Examples\n")
                for example in module.examples:
                    docs.append("```python")
                    docs.append(example.strip())
                    docs.append("```\n")
            
            docs.append("---\n")
        
        return "\n".join(docs)
    
    def get_module_info(self, module_name: str) -> Optional[APIModule]:
        """Get information about a specific module."""
        return self.modules.get(module_name)
    
    def list_modules(self) -> List[str]:
        """List all available modules."""
        return list(self.modules.keys())
    
    def search_endpoints(self, query: str) -> List[APIEndpoint]:
        """Search for endpoints matching a query."""
        results = []
        query_lower = query.lower()
        
        for module in self.modules.values():
            for endpoint in module.endpoints:
                if (query_lower in endpoint.name.lower() or 
                    query_lower in endpoint.description.lower()):
                    results.append(endpoint)
        
        return results


def generate_api_docs():
    """Generate and save API documentation."""
    generator = APIDocumentationGenerator()
    markdown_docs = generator.generate_markdown_docs()
    
    # Save to file
    with open("API_REFERENCE.md", "w", encoding="utf-8") as f:
        f.write(markdown_docs)
    
    logger.debug("📚 API documentation generated: API_REFERENCE.md")
    return markdown_docs


if __name__ == "__main__":
    # Generate documentation when run as script
    docs = generate_api_docs()
    logger.debug("\n" + "="*60)
    logger.debug("API DOCUMENTATION PREVIEW")
    logger.debug("="*60)
    print(docs[:2000] + "..." if len(docs) > 2000 else docs) 