"""
Phase 6.1: Core Sync Engine
===========================

This module implements the core synchronization engine for bidirectional sync
between PST files and Dynamics 365, with change tracking and conflict detection.
"""

import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SyncState:
    """Represents the synchronization state of an item"""
    item_id: str
    source_hash: str
    target_hash: str
    last_sync: datetime
    status: str
    conflicts: List[Dict[str, Any]] = None

class ConflictResolver:
    """Advanced conflict resolution system supporting multiple strategies and history."""
    def __init__(self):
        self.resolution_strategies = {
            'last_write_wins': self.last_write_wins,
            'manual': self.manual_resolution,
            'merge': self.merge_changes
        }
        self.conflict_history = []

    def resolve(self, conflict, strategy='last_write_wins', user_choice=None):
        """Resolve a conflict using the specified strategy."""
        if strategy not in self.resolution_strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        result = self.resolution_strategies[strategy](conflict, user_choice)
        self.conflict_history.append({
            'conflict': conflict,
            'strategy': strategy,
            'result': result,
            'timestamp': datetime.now()
        })
        return result

    def last_write_wins(self, conflict, user_choice=None):
        # For demo, always use source value
        return conflict['change']['source_value']

    def manual_resolution(self, conflict, user_choice=None):
        # Simulate manual resolution (user_choice must be provided)
        if user_choice is None:
            raise ValueError("Manual resolution requires user_choice.")
        return user_choice

    def merge_changes(self, conflict, user_choice=None):
        # For demo, just concatenate string values if both are strings
        src = conflict['change']['source_value']
        tgt = conflict['change']['target_value']
        if isinstance(src, str) and isinstance(tgt, str):
            return src + ' / ' + tgt
        return src or tgt

    def get_conflict_history(self):
        return self.conflict_history

class SyncMonitor:
    """Tracks sync events, metrics, and errors."""
    def __init__(self):
        self.metrics = {
            'sync_count': 0,
            'conflict_count': 0,
            'error_count': 0
        }
        self.logs = []

    def track_sync(self, sync_event: str, details: dict = None):
        self.metrics['sync_count'] += 1
        self.logs.append({'event': sync_event, 'details': details, 'timestamp': datetime.now()})

    def track_conflict(self, conflict):
        self.metrics['conflict_count'] += 1
        self.logs.append({'event': 'conflict', 'details': conflict, 'timestamp': datetime.now()})

    def track_error(self, error):
        self.metrics['error_count'] += 1
        self.logs.append({'event': 'error', 'details': error, 'timestamp': datetime.now()})

    def get_metrics(self):
        return self.metrics

    def get_logs(self):
        return self.logs

class SyncEngine:
    """Core synchronization engine for PST to Dynamics 365 sync"""
    
    def __init__(self):
        """Initialize the sync engine with required components"""
        self.sync_state: Dict[str, SyncState] = {}
        self.change_tracker = ChangeTracker()
        self.conflict_detector = ConflictDetector()
        self.validator = DataValidator()
        self.conflict_resolver = ConflictResolver()
        self.monitor = SyncMonitor()
        
        logger.info("Sync Engine initialized")
    
    def sync_data(self, source_data: Dict[str, Any], target_data: Dict[str, Any], strategy='last_write_wins', manual_choices=None) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        """
        Synchronize data between source and target using last-write-wins for conflicts.
        Returns updated (source_data, target_data, conflicts)
        """
        # Track changes
        changes = self.change_tracker.track_changes(source_data, target_data)
        # Detect conflicts
        conflicts = self.conflict_detector.detect_conflicts(changes)
        # Apply last-write-wins for all fields
        manual_choices = manual_choices or {}
        for conflict in conflicts:
            field = conflict['change']['field']
            if strategy == 'manual':
                user_choice = manual_choices.get(field)
                resolved_value = self.conflict_resolver.resolve(conflict, strategy, user_choice)
            else:
                resolved_value = self.conflict_resolver.resolve(conflict, strategy)
            target_data[field] = resolved_value
            self.monitor.track_conflict(conflict)
        # Validate
        valid_source = self.validator.validate_data(source_data)
        valid_target = self.validator.validate_data(target_data)
        if not (valid_source and valid_target):
            logger.error("Validation failed during sync.")
            self.monitor.track_error("Validation failed")
        # Update sync state
        self._update_sync_state(source_data, target_data)
        self.monitor.track_sync('sync', {'source': source_data['id'], 'target': target_data['id']})
        return source_data, target_data, conflicts
    
    def _update_sync_state(self, source_data: Dict[str, Any], target_data: Dict[str, Any]):
        """Update the sync state for an item"""
        item_id = source_data.get('id') or target_data.get('id')
        if not item_id:
            return
        
        source_hash = self._generate_hash(source_data)
        target_hash = self._generate_hash(target_data)
        
        self.sync_state[item_id] = SyncState(
            item_id=item_id,
            source_hash=source_hash,
            target_hash=target_hash,
            last_sync=datetime.now(),
            status='synced'
        )
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate a hash for data comparison"""
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get_sync_status(self, item_id: str) -> Optional[SyncState]:
        """Get the sync status for an item"""
        return self.sync_state.get(item_id)
    
    def get_all_sync_states(self) -> List[SyncState]:
        """Get all sync states"""
        return list(self.sync_state.values())

    def recover_sync(self, item_id: str) -> bool:
        """Attempt to recover a failed sync by restoring last known good state."""
        state = self.sync_state.get(item_id)
        if not state:
            logger.error(f"No sync state found for {item_id}")
            return False
        # For demo, just log recovery
        logger.info(f"Recovered sync for {item_id} to state at {state.last_sync}")
        return True

class ChangeTracker:
    """Tracks changes between source and target data"""
    
    def track_changes(self, source_data: Dict[str, Any], target_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Track changes between source and target data"""
        changes = []
        
        # Compare all fields
        all_keys = set(source_data.keys()) | set(target_data.keys())
        
        for key in all_keys:
            source_value = source_data.get(key)
            target_value = target_data.get(key)
            
            if source_value != target_value:
                changes.append({
                    'field': key,
                    'source_value': source_value,
                    'target_value': target_value,
                    'timestamp': datetime.now()
                })
        
        return changes

class ConflictDetector:
    """Detects conflicts in synchronized data"""
    
    def detect_conflicts(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect conflicts in the changes"""
        conflicts = []
        
        for change in changes:
            # Check for potential conflicts
            if self._is_conflict(change):
                conflicts.append({
                    'change': change,
                    'type': self._determine_conflict_type(change),
                    'timestamp': datetime.now()
                })
        
        return conflicts
    
    def _is_conflict(self, change: Dict[str, Any]) -> bool:
        """Determine if a change represents a conflict"""
        # Implement conflict detection logic
        # For now, consider all changes as potential conflicts
        return True
    
    def _determine_conflict_type(self, change: Dict[str, Any]) -> str:
        """Determine the type of conflict"""
        # Implement conflict type determination
        return 'data_mismatch'

class DataValidator:
    """Validates data integrity during sync, with checksums and consistency checks."""
    def __init__(self):
        self.validation_rules = {
            'required_fields': ['id', 'name', 'email'],
            'email_format': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }
        self.checksums = {}

    def validate_data(self, data: Dict[str, Any]) -> bool:
        try:
            for field in self.validation_rules['required_fields']:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            if 'email' in data:
                import re
                if not re.match(self.validation_rules['email_format'], data['email']):
                    logger.error(f"Invalid email format: {data['email']}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False

    def generate_checksum(self, data: Dict[str, Any]) -> str:
        """Generate a checksum for the given data."""
        import hashlib
        data_str = str(sorted(data.items()))
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        return checksum

    def verify_checksum(self, data: Dict[str, Any], checksum: str) -> bool:
        """Verify that the checksum matches the data."""
        return self.generate_checksum(data) == checksum

    def check_consistency(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> bool:
        """Check if two data dicts are consistent (all fields match)."""
        return data1 == data2

# --- Integration Stubs ---
class PSTDataSource:
    """Stub for PST data source integration."""
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        # TODO: Implement actual PST reading
        return {'id': contact_id, 'name': 'PST User', 'email': 'pst@example.com'}

class DynamicsDataSource:
    """Stub for Dynamics 365 data source integration."""
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        # TODO: Implement actual Dynamics 365 API call
        return {'id': contact_id, 'name': 'Dynamics User', 'email': 'dynamics@example.com'}

# Stub for dashboard/reporting interface
class SyncDashboard:
    """Stub for a future GUI dashboard/reporting interface."""
    def __init__(self, monitor: SyncMonitor):
        self.monitor = monitor
    def display_metrics(self):
        print("Sync Metrics:", self.monitor.get_metrics())
    def display_logs(self):
        for log in self.monitor.get_logs():
            print(log) 