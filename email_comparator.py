"""
Email Comparator Module
======================

Advanced email comparison and duplicate detection for Phase 2.
Uses multiple strategies to identify duplicate emails with high accuracy.

Author: AI Assistant
Phase: 2
"""

import re
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import config

class EmailComparator:
    """Advanced email comparison and duplicate detection."""
    
    def __init__(self):
        """Initialize the email comparator."""
        self.logger = logging.getLogger(__name__)
        
        # Comparison settings from config
        self.use_message_id = config.ADVANCED_COMPARISON['USE_MESSAGE_ID']
        self.use_content_hash = config.ADVANCED_COMPARISON['USE_CONTENT_HASH']
        self.fuzzy_timestamp_minutes = config.ADVANCED_COMPARISON['FUZZY_TIMESTAMP_MINUTES']
        self.subject_similarity_threshold = config.ADVANCED_COMPARISON['SUBJECT_SIMILARITY_THRESHOLD']
        self.content_similarity_threshold = config.ADVANCED_COMPARISON['CONTENT_SIMILARITY_THRESHOLD']
        
        # Statistics tracking
        self.comparison_stats = {
            'total_comparisons': 0,
            'message_id_matches': 0,
            'content_hash_matches': 0,
            'fuzzy_timestamp_matches': 0,
            'subject_similarity_matches': 0,
            'sender_recipient_matches': 0,
            'no_matches': 0
        }
    
    def find_duplicates(self, pst_email: Dict, dynamics_emails: List[Dict]) -> Dict:
        """
        Find duplicates of a PST email in existing Dynamics emails.
        
        Args:
            pst_email: Email from PST file
            dynamics_emails: List of existing emails in Dynamics
            
        Returns:
            Dict with duplicate analysis results
        """
        self.comparison_stats['total_comparisons'] += 1
        
        duplicates = []
        best_match = None
        best_confidence = 0.0
        
        for dynamics_email in dynamics_emails:
            match_result = self._compare_emails(pst_email, dynamics_email)
            
            if match_result['is_duplicate']:
                duplicates.append({
                    'dynamics_email': dynamics_email,
                    'match_confidence': match_result['confidence'],
                    'match_reasons': match_result['reasons']
                })
                
                # Track best match
                if match_result['confidence'] > best_confidence:
                    best_confidence = match_result['confidence']
                    best_match = dynamics_email
        
        result = {
            'has_duplicates': len(duplicates) > 0,
            'duplicate_count': len(duplicates),
            'duplicates': duplicates,
            'best_match': best_match,
            'best_confidence': best_confidence
        }
        
        # Update statistics
        if not result['has_duplicates']:
            self.comparison_stats['no_matches'] += 1
        
        return result
    
    def _compare_emails(self, email1: Dict, email2: Dict) -> Dict:
        """
        Compare two emails using multiple strategies.
        
        Args:
            email1: First email for comparison
            email2: Second email for comparison
            
        Returns:
            Dict with comparison results
        """
        reasons = []
        confidence = 0.0
        is_duplicate = False
        
        # Strategy 1: Message-ID header matching (highest confidence)
        if self.use_message_id:
            message_id_match = self._compare_by_message_id(email1, email2)
            if message_id_match['match']:
                reasons.append('Message-ID header match')
                confidence = 1.0  # 100% confidence for Message-ID match
                is_duplicate = True
                self.comparison_stats['message_id_matches'] += 1
                return {
                    'is_duplicate': is_duplicate,
                    'confidence': confidence,
                    'reasons': reasons
                }
        
        # Strategy 2: Content hash matching (high confidence)
        if self.use_content_hash:
            content_hash_match = self._compare_by_content_hash(email1, email2)
            if content_hash_match['match']:
                reasons.append('Content hash match')
                confidence = max(confidence, 0.95)  # 95% confidence
                is_duplicate = True
                self.comparison_stats['content_hash_matches'] += 1
        
        # Strategy 3: Fuzzy timestamp + subject matching (medium confidence)
        timestamp_match = self._fuzzy_timestamp_matching(email1, email2)
        subject_match = self._subject_similarity_check(email1, email2)
        
        if timestamp_match['match'] and subject_match['match']:
            reasons.append(f'Timestamp + subject match (similarity: {subject_match["similarity"]:.2f})')
            confidence = max(confidence, 0.85)  # 85% confidence
            is_duplicate = True
            self.comparison_stats['fuzzy_timestamp_matches'] += 1
            self.comparison_stats['subject_similarity_matches'] += 1
        
        # Strategy 4: Sender + recipient + timestamp (medium confidence)
        sender_recipient_match = self._sender_recipient_matching(email1, email2)
        if sender_recipient_match['match'] and timestamp_match['match']:
            reasons.append('Sender + recipient + timestamp match')
            confidence = max(confidence, 0.80)  # 80% confidence
            is_duplicate = True
            self.comparison_stats['sender_recipient_matches'] += 1
        
        # Strategy 5: Content similarity (lower confidence)
        content_similarity = self._content_similarity_check(email1, email2)
        if content_similarity['match']:
            reasons.append(f'Content similarity match ({content_similarity["similarity"]:.2f})')
            confidence = max(confidence, 0.75)  # 75% confidence
            is_duplicate = True
        
        # Final duplicate determination (require minimum confidence)
        if confidence >= 0.75:
            is_duplicate = True
        
        return {
            'is_duplicate': is_duplicate,
            'confidence': confidence,
            'reasons': reasons
        }
    
    def _compare_by_message_id(self, email1: Dict, email2: Dict) -> Dict:
        """Compare emails by Message-ID header."""
        message_id1 = self._extract_message_id(email1)
        message_id2 = self._extract_message_id(email2)
        
        if message_id1 and message_id2:
            match = message_id1.lower() == message_id2.lower()
            return {
                'match': match,
                'message_id1': message_id1,
                'message_id2': message_id2
            }
        
        return {'match': False, 'message_id1': None, 'message_id2': None}
    
    def _extract_message_id(self, email: Dict) -> Optional[str]:
        """Extract Message-ID from email headers."""
        # Try different possible header fields
        headers = email.get('headers', {})
        
        # Check common Message-ID field names
        for field in ['Message-ID', 'message-id', 'MessageID', 'message_id']:
            if field in headers:
                message_id = headers[field]
                # Clean up Message-ID (remove < > brackets)
                if message_id:
                    return message_id.strip('<>')
        
        # Try extracting from raw headers if available
        raw_headers = email.get('raw_headers', '')
        if raw_headers:
            match = re.search(r'Message-ID:\s*<?(.*?)>?\r?\n', raw_headers, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _compare_by_content_hash(self, email1: Dict, email2: Dict) -> Dict:
        """Compare emails by content hash."""
        hash1 = self._calculate_content_hash(email1)
        hash2 = self._calculate_content_hash(email2)
        
        match = hash1 == hash2 if hash1 and hash2 else False
        
        return {
            'match': match,
            'hash1': hash1,
            'hash2': hash2
        }
    
    def _calculate_content_hash(self, email: Dict) -> Optional[str]:
        """Calculate a hash of email content for comparison."""
        try:
            # Combine key content fields
            content_parts = []
            
            # Add subject (normalized)
            subject = email.get('subject', '').strip().lower()
            if subject:
                content_parts.append(subject)
            
            # Add body (normalized)
            body = email.get('body', '').strip().lower()
            if body:
                # Remove extra whitespace and common formatting
                body_normalized = re.sub(r'\s+', ' ', body)
                body_normalized = re.sub(r'[^\w\s]', '', body_normalized)
                content_parts.append(body_normalized)
            
            # Add sender email
            sender_email = email.get('sender_email', '').strip().lower()
            if sender_email:
                content_parts.append(sender_email)
            
            if content_parts:
                content_string = '|'.join(content_parts)
                return hashlib.md5(content_string.encode('utf-8')).hexdigest()
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error calculating content hash: {e}")
            return None
    
    def _fuzzy_timestamp_matching(self, email1: Dict, email2: Dict) -> Dict:
        """Compare emails with fuzzy timestamp matching."""
        try:
            # Extract timestamps
            timestamp1 = self._parse_timestamp(email1.get('sent_time'))
            timestamp2 = self._parse_timestamp(email2.get('sent_time') or email2.get('actualstart'))
            
            if timestamp1 and timestamp2:
                # Calculate time difference
                time_diff = abs((timestamp1 - timestamp2).total_seconds()) / 60  # minutes
                
                match = time_diff <= self.fuzzy_timestamp_minutes
                
                return {
                    'match': match,
                    'time_difference_minutes': time_diff,
                    'timestamp1': timestamp1,
                    'timestamp2': timestamp2
                }
            
            return {'match': False, 'time_difference_minutes': None}
            
        except Exception as e:
            self.logger.warning(f"Error in fuzzy timestamp matching: {e}")
            return {'match': False, 'time_difference_minutes': None}
    
    def _parse_timestamp(self, timestamp: Union[str, datetime, None]) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if not timestamp:
            return None
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            # Try common timestamp formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with microseconds
                '%Y-%m-%dT%H:%M:%SZ',     # ISO format
                '%Y-%m-%dT%H:%M:%S',      # ISO format without Z
                '%Y-%m-%d %H:%M:%S',      # Standard format
                '%m/%d/%Y %H:%M:%S',      # US format
                '%d/%m/%Y %H:%M:%S'       # European format
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _subject_similarity_check(self, email1: Dict, email2: Dict) -> Dict:
        """Check subject similarity between emails."""
        subject1 = email1.get('subject', '').strip()
        subject2 = email2.get('subject', '').strip()
        
        if not subject1 or not subject2:
            return {'match': False, 'similarity': 0.0}
        
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, subject1.lower(), subject2.lower()).ratio()
        
        match = similarity >= self.subject_similarity_threshold
        
        return {
            'match': match,
            'similarity': similarity,
            'subject1': subject1,
            'subject2': subject2
        }
    
    def _sender_recipient_matching(self, email1: Dict, email2: Dict) -> Dict:
        """Match emails by sender and recipient combination."""
        sender1 = email1.get('sender_email', '').strip().lower()
        sender2 = email2.get('sender_email', '').strip().lower()
        
        # For Dynamics emails, extract sender from activity party or description
        if not sender2 and 'description' in email2:
            # Try to extract from "Email from: xxx" in description
            match = re.search(r'Email from:\s*([^\s]+)', email2['description'])
            if match:
                sender2 = match.group(1).strip().lower()
        
        recipient1 = email1.get('recipient_email', config.USERNAME.lower())
        recipient2 = email2.get('recipient_email', config.USERNAME.lower())
        
        sender_match = sender1 == sender2 if sender1 and sender2 else False
        recipient_match = recipient1 == recipient2 if recipient1 and recipient2 else True  # Default match
        
        match = sender_match and recipient_match
        
        return {
            'match': match,
            'sender_match': sender_match,
            'recipient_match': recipient_match,
            'sender1': sender1,
            'sender2': sender2,
            'recipient1': recipient1,
            'recipient2': recipient2
        }
    
    def _content_similarity_check(self, email1: Dict, email2: Dict) -> Dict:
        """Check content similarity between email bodies."""
        body1 = email1.get('body', '').strip()
        body2 = email2.get('body', '').strip()
        
        if not body1 or not body2:
            return {'match': False, 'similarity': 0.0}
        
        # Normalize content for comparison
        body1_normalized = self._normalize_content(body1)
        body2_normalized = self._normalize_content(body2)
        
        # Calculate similarity
        similarity = SequenceMatcher(None, body1_normalized, body2_normalized).ratio()
        
        match = similarity >= self.content_similarity_threshold
        
        return {
            'match': match,
            'similarity': similarity
        }
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for comparison."""
        # Convert to lowercase
        content = content.lower()
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove special characters
        content = re.sub(r'[^\w\s]', '', content)
        
        return content.strip()
    
    def get_comparison_stats(self) -> Dict:
        """Get comparison statistics."""
        return self.comparison_stats.copy()
    
    def reset_stats(self):
        """Reset comparison statistics."""
        self.comparison_stats = {
            'total_comparisons': 0,
            'message_id_matches': 0,
            'content_hash_matches': 0,
            'fuzzy_timestamp_matches': 0,
            'subject_similarity_matches': 0,
            'sender_recipient_matches': 0,
            'no_matches': 0
        } 