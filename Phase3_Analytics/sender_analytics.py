#!/usr/bin/env python3
"""
Sender Analytics & Communication Intelligence
===========================================

Phase 3.3 - Advanced sender analysis and communication pattern recognition.
Provides insights into communication relationships, sender importance,
and communication network analysis.

Features:
- Sender profiling and classification
- Communication pattern analysis
- Relationship strength scoring
- Email volume trend analysis
- Response time analytics
- Communication network mapping
- Sender importance ranking
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics
import re

# Add parent directory to path for imports
sys.path.append('..')
from config import *


@dataclass
class SenderProfile:
    """Complete profile of an email sender."""
    sender_email: str
    sender_name: Optional[str]
    classification: str  # 'high_priority_client', 'colleague', 'vendor', 'automated', 'unknown'
    confidence_score: float  # 0-1 confidence in classification
    metrics: Dict[str, Any]
    trends: Dict[str, Any]
    relationship_strength: float  # 0-10 scale
    importance_score: float  # 0-10 scale
    communication_pattern: Dict[str, Any]
    contact_info: Optional[Dict[str, str]]


@dataclass
class CommunicationRelationship:
    """Represents a communication relationship between two parties."""
    sender_email: str
    recipient_email: str
    total_emails: int
    date_range: Tuple[date, date]
    avg_emails_per_month: float
    response_patterns: Dict[str, Any]
    relationship_type: str
    strength_score: float


@dataclass
class SenderAnalysisResults:
    """Complete sender analysis results."""
    analysis_date: datetime
    total_senders: int
    sender_profiles: List[SenderProfile]
    communication_relationships: List[CommunicationRelationship]
    network_statistics: Dict[str, Any]
    top_senders: List[Tuple[str, int]]
    recommendations: List[str]


class SenderAnalyzer:
    """Analyzes email senders to provide communication intelligence."""
    
    def __init__(self):
        # Classification patterns
        self.domain_patterns = {
            'internal': ['.local', 'company.com', 'organization.com'],
            'automated': ['noreply', 'no-reply', 'donotreply', 'automated', 'system'],
            'service': ['service@', 'support@', 'help@', 'notifications@'],
            'marketing': ['marketing@', 'newsletter@', 'promotions@', 'offers@']
        }
        
        # Importance scoring factors
        self.importance_factors = {
            'email_volume': 0.3,
            'communication_frequency': 0.2,
            'response_patterns': 0.2,
            'domain_authority': 0.15,
            'name_recognition': 0.15
        }
        
        print("👥 Sender Analytics Engine initialized")
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if '@' in email:
            return email.split('@')[1].lower()
        return ''
    
    def _classify_sender_type(self, email: str, name: str = None) -> Tuple[str, float]:
        """Classify sender type with confidence score."""
        email_lower = email.lower()
        domain = self._extract_domain(email)
        
        # Check for automated/system emails
        automated_keywords = ['noreply', 'no-reply', 'donotreply', 'automated', 'system', 'bot']
        if any(keyword in email_lower for keyword in automated_keywords):
            return 'automated', 0.9
        
        # Check for service emails
        service_keywords = ['service', 'support', 'help', 'notifications', 'admin', 'security']
        if any(keyword in email_lower for keyword in service_keywords):
            return 'service', 0.8
        
        # Check for marketing emails
        marketing_keywords = ['marketing', 'newsletter', 'promotions', 'offers', 'campaign']
        if any(keyword in email_lower for keyword in marketing_keywords):
            return 'marketing', 0.8
        
        # Check if it's likely a personal/professional contact
        if name and self._is_personal_name(name):
            # Determine if colleague or external based on domain patterns
            if any(pattern in domain for pattern in self.domain_patterns.get('internal', [])):
                return 'colleague', 0.7
            else:
                return 'external_contact', 0.6
        
        # Check for vendor/business patterns
        business_keywords = ['sales', 'account', 'billing', 'invoice', 'orders']
        if any(keyword in email_lower for keyword in business_keywords):
            return 'vendor', 0.6
        
        return 'unknown', 0.3
    
    def _is_personal_name(self, name: str) -> bool:
        """Check if a name appears to be a personal name."""
        if not name:
            return False
        
        # Simple heuristics for personal names
        words = name.split()
        if len(words) >= 2:  # First and last name
            # Check if words contain mostly letters
            letter_ratio = sum(c.isalpha() for c in name) / len(name)
            return letter_ratio > 0.7
        
        return False
    
    def _calculate_relationship_strength(self, email_count: int, date_range_days: int, 
                                       response_patterns: Dict) -> float:
        """Calculate relationship strength score (0-10)."""
        if date_range_days == 0:
            return 0.0
        
        # Base score from email frequency
        emails_per_month = (email_count / date_range_days) * 30
        frequency_score = min(10, emails_per_month / 5)  # 5 emails/month = score of 2
        
        # Adjust for consistency
        consistency_bonus = response_patterns.get('consistency_score', 0.5) * 2
        
        # Adjust for recency
        last_contact_days = response_patterns.get('days_since_last_contact', 365)
        recency_factor = max(0.1, 1 - (last_contact_days / 365))
        
        total_score = (frequency_score + consistency_bonus) * recency_factor
        return min(10.0, max(0.0, total_score))
    
    def _calculate_importance_score(self, profile_data: Dict) -> float:
        """Calculate sender importance score (0-10)."""
        score = 0.0
        
        # Email volume factor
        email_count = profile_data.get('total_emails', 0)
        volume_score = min(5, email_count / 20)  # 20 emails = score of 1
        score += volume_score * self.importance_factors['email_volume']
        
        # Communication frequency factor
        freq_score = profile_data.get('avg_emails_per_month', 0)
        frequency_score = min(5, freq_score / 2)  # 2 emails/month = score of 1
        score += frequency_score * self.importance_factors['communication_frequency']
        
        # Response pattern factor (if bidirectional communication)
        response_score = profile_data.get('response_rate', 0) * 5
        score += response_score * self.importance_factors['response_patterns']
        
        # Domain authority (external domains might be more important)
        domain_score = 3 if profile_data.get('sender_type') == 'external_contact' else 2
        score += domain_score * self.importance_factors['domain_authority']
        
        # Name recognition (personal names might be more important)
        name_score = 4 if profile_data.get('has_personal_name', False) else 2
        score += name_score * self.importance_factors['name_recognition']
        
        return min(10.0, max(0.0, score))
    
    def _analyze_communication_pattern(self, email_dates: List[date]) -> Dict[str, Any]:
        """Analyze communication patterns for a sender."""
        if not email_dates:
            return {'pattern_type': 'no_data'}
        
        sorted_dates = sorted(email_dates)
        
        # Calculate time intervals
        intervals = []
        for i in range(1, len(sorted_dates)):
            interval = (sorted_dates[i] - sorted_dates[i-1]).days
            intervals.append(interval)
        
        if not intervals:
            return {'pattern_type': 'single_email'}
        
        # Analyze patterns
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        median_interval = statistics.median(intervals)
        
        # Determine pattern type
        consistency = 1 - (std_interval / avg_interval) if avg_interval > 0 else 0
        
        if consistency > 0.8 and avg_interval <= 7:
            pattern_type = 'regular_frequent'
        elif consistency > 0.6 and avg_interval <= 30:
            pattern_type = 'regular_moderate'
        elif avg_interval <= 3:
            pattern_type = 'burst_communication'
        elif avg_interval >= 90:
            pattern_type = 'sporadic'
        else:
            pattern_type = 'irregular'
        
        # Day of week analysis
        day_counts = Counter(date.weekday() for date in sorted_dates)
        most_common_day = day_counts.most_common(1)[0][0]
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'pattern_type': pattern_type,
            'consistency_score': round(consistency, 2),
            'avg_interval_days': round(avg_interval, 1),
            'median_interval_days': median_interval,
            'total_span_days': (sorted_dates[-1] - sorted_dates[0]).days,
            'most_active_day': day_names[most_common_day],
            'weekend_ratio': (day_counts[5] + day_counts[6]) / len(sorted_dates),
            'email_frequency': 'high' if avg_interval < 7 else 'medium' if avg_interval < 30 else 'low'
        }
    
    def analyze_sender(self, sender_email: str, email_data: List[Dict]) -> SenderProfile:
        """Analyze a single sender to create complete profile."""
        if not email_data:
            return SenderProfile(
                sender_email=sender_email,
                sender_name=None,
                classification='unknown',
                confidence_score=0.0,
                metrics={},
                trends={},
                relationship_strength=0.0,
                importance_score=0.0,
                communication_pattern={},
                contact_info=None
            )
        
        # Extract basic information
        sender_names = [email.get('sender_name', '') for email in email_data if email.get('sender_name')]
        most_common_name = Counter(sender_names).most_common(1)[0][0] if sender_names else None
        
        # Extract email dates
        email_dates = []
        for email in email_data:
            if email.get('date'):
                try:
                    if isinstance(email['date'], str):
                        email_date = datetime.fromisoformat(email['date']).date()
                    else:
                        email_date = email['date']
                    email_dates.append(email_date)
                except:
                    pass
        
        # Classify sender
        classification, confidence = self._classify_sender_type(sender_email, most_common_name)
        
        # Calculate metrics
        total_emails = len(email_data)
        date_range = (min(email_dates), max(email_dates)) if email_dates else (date.today(), date.today())
        timeline_days = (date_range[1] - date_range[0]).days + 1
        
        metrics = {
            'total_emails': total_emails,
            'date_range': date_range,
            'timeline_days': timeline_days,
            'avg_emails_per_month': (total_emails / timeline_days * 30) if timeline_days > 0 else 0,
            'first_contact': date_range[0],
            'last_contact': date_range[1],
            'days_since_last_contact': (date.today() - date_range[1]).days if email_dates else 365,
            'has_personal_name': self._is_personal_name(most_common_name or ''),
            'sender_type': classification,
            'domain': self._extract_domain(sender_email)
        }
        
        # Analyze communication patterns
        communication_pattern = self._analyze_communication_pattern(email_dates)
        
        # Calculate relationship strength
        response_patterns = {
            'consistency_score': communication_pattern.get('consistency_score', 0.5),
            'days_since_last_contact': metrics['days_since_last_contact']
        }
        relationship_strength = self._calculate_relationship_strength(
            total_emails, timeline_days, response_patterns
        )
        
        # Calculate importance score
        importance_score = self._calculate_importance_score(metrics)
        
        # Analyze trends (simplified)
        trends = {
            'communication_trend': 'stable',  # Would need more complex analysis
            'response_time_trend': 'unknown',
            'volume_trend': 'stable'
        }
        
        # Contact information (extract from email data if available)
        contact_info = {
            'email': sender_email,
            'name': most_common_name,
            'domain': metrics['domain']
        }
        
        return SenderProfile(
            sender_email=sender_email,
            sender_name=most_common_name,
            classification=classification,
            confidence_score=confidence,
            metrics=metrics,
            trends=trends,
            relationship_strength=relationship_strength,
            importance_score=importance_score,
            communication_pattern=communication_pattern,
            contact_info=contact_info
        )
    
    def analyze_all_senders(self, emails_by_sender: Dict[str, List[Dict]]) -> SenderAnalysisResults:
        """Analyze all senders to provide comprehensive insights."""
        print(f"👥 Analyzing {len(emails_by_sender)} senders...")
        
        sender_profiles = []
        total_emails = 0
        
        # Analyze each sender
        for sender_email, email_data in emails_by_sender.items():
            profile = self.analyze_sender(sender_email, email_data)
            sender_profiles.append(profile)
            total_emails += len(email_data)
        
        # Sort by importance
        sender_profiles.sort(key=lambda p: p.importance_score, reverse=True)
        
        # Generate top senders list
        top_senders = [(p.sender_email, p.metrics['total_emails']) for p in sender_profiles[:10]]
        
        # Calculate network statistics
        network_stats = self._calculate_network_statistics(sender_profiles, total_emails)
        
        # Generate communication relationships (simplified)
        relationships = self._generate_relationships(sender_profiles)
        
        # Generate recommendations
        recommendations = self._generate_sender_recommendations(sender_profiles, network_stats)
        
        return SenderAnalysisResults(
            analysis_date=datetime.now(),
            total_senders=len(sender_profiles),
            sender_profiles=sender_profiles,
            communication_relationships=relationships,
            network_statistics=network_stats,
            top_senders=top_senders,
            recommendations=recommendations
        )
    
    def _calculate_network_statistics(self, profiles: List[SenderProfile], total_emails: int) -> Dict[str, Any]:
        """Calculate overall network communication statistics."""
        if not profiles:
            return {}
        
        # Classification distribution
        classifications = Counter(p.classification for p in profiles)
        
        # Importance distribution
        high_importance = len([p for p in profiles if p.importance_score >= 7])
        medium_importance = len([p for p in profiles if 4 <= p.importance_score < 7])
        low_importance = len([p for p in profiles if p.importance_score < 4])
        
        # Communication patterns
        pattern_types = Counter(p.communication_pattern.get('pattern_type', 'unknown') for p in profiles)
        
        # Domain analysis
        domains = Counter(p.metrics.get('domain', 'unknown') for p in profiles)
        
        return {
            'total_senders': len(profiles),
            'total_emails_analyzed': total_emails,
            'classification_distribution': dict(classifications),
            'importance_distribution': {
                'high': high_importance,
                'medium': medium_importance,
                'low': low_importance
            },
            'pattern_distribution': dict(pattern_types),
            'top_domains': dict(domains.most_common(10)),
            'avg_importance_score': round(statistics.mean(p.importance_score for p in profiles), 2),
            'avg_relationship_strength': round(statistics.mean(p.relationship_strength for p in profiles), 2),
            'high_value_contacts': len([p for p in profiles if p.importance_score >= 8]),
            'active_contacts': len([p for p in profiles if p.metrics.get('days_since_last_contact', 365) <= 30])
        }
    
    def _generate_relationships(self, profiles: List[SenderProfile]) -> List[CommunicationRelationship]:
        """Generate communication relationship analysis (simplified)."""
        relationships = []
        
        # For now, create basic relationships for high-importance senders
        for profile in profiles[:20]:  # Top 20 senders
            if profile.metrics.get('total_emails', 0) > 5:
                relationship = CommunicationRelationship(
                    sender_email=profile.sender_email,
                    recipient_email="current_user",  # Placeholder
                    total_emails=profile.metrics['total_emails'],
                    date_range=profile.metrics['date_range'],
                    avg_emails_per_month=profile.metrics['avg_emails_per_month'],
                    response_patterns={'estimated_response_rate': 0.5},  # Placeholder
                    relationship_type=profile.classification,
                    strength_score=profile.relationship_strength
                )
                relationships.append(relationship)
        
        return relationships
    
    def _generate_sender_recommendations(self, profiles: List[SenderProfile], 
                                       network_stats: Dict) -> List[str]:
        """Generate actionable recommendations based on sender analysis."""
        recommendations = []
        
        # High-value contacts
        high_value = [p for p in profiles if p.importance_score >= 8]
        if high_value:
            recommendations.append(f"Found {len(high_value)} high-value contacts - ensure timeline completeness for these senders")
        
        # Inactive important contacts
        inactive_important = [p for p in profiles 
                            if p.importance_score >= 6 and p.metrics.get('days_since_last_contact', 0) > 90]
        if inactive_important:
            recommendations.append(f"{len(inactive_important)} important contacts have been inactive for 90+ days - consider reaching out")
        
        # Automated email volume
        automated_count = network_stats['classification_distribution'].get('automated', 0)
        total_senders = network_stats['total_senders']
        if automated_count > total_senders * 0.3:
            recommendations.append(f"High volume of automated emails ({automated_count}) - consider filtering during import")
        
        # Unknown classifications
        unknown_count = network_stats['classification_distribution'].get('unknown', 0)
        if unknown_count > total_senders * 0.2:
            recommendations.append(f"{unknown_count} senders could not be classified - manual review recommended")
        
        # Pattern insights
        if 'burst_communication' in network_stats['pattern_distribution']:
            burst_count = network_stats['pattern_distribution']['burst_communication']
            recommendations.append(f"{burst_count} senders show burst communication patterns - may indicate project-based relationships")
        
        return recommendations
    
    def export_analysis(self, analysis: SenderAnalysisResults, format_type: str = "json") -> str:
        """Export sender analysis in specified format."""
        if format_type.lower() == "json":
            return json.dumps(asdict(analysis), indent=2, default=str)
        elif format_type.lower() == "csv":
            return self._export_to_csv(analysis)
        else:
            return str(asdict(analysis))
    
    def _export_to_csv(self, analysis: SenderAnalysisResults) -> str:
        """Export analysis to CSV format."""
        lines = []
        lines.append("Sender Email,Sender Name,Classification,Confidence,Total Emails,Importance Score,Relationship Strength,Last Contact,Pattern Type")
        
        for profile in analysis.sender_profiles:
            line = f"{profile.sender_email},{profile.sender_name or ''},{profile.classification},{profile.confidence_score},{profile.metrics.get('total_emails', 0)},{profile.importance_score:.1f},{profile.relationship_strength:.1f},{profile.metrics.get('last_contact', '')},{profile.communication_pattern.get('pattern_type', '')}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def save_analysis_to_db(self, analysis: SenderAnalysisResults, 
                          db_path: str = "Phase3_Analytics/sender_analysis.db"):
        """Save analysis results to database."""
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sender_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TEXT NOT NULL,
                total_senders INTEGER,
                network_statistics TEXT,
                recommendations TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sender_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                sender_email TEXT NOT NULL,
                sender_name TEXT,
                classification TEXT,
                confidence_score REAL,
                importance_score REAL,
                relationship_strength REAL,
                metrics TEXT,
                trends TEXT,
                communication_pattern TEXT,
                contact_info TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES sender_analysis (id)
            )
        """)
        
        # Insert analysis record
        cursor.execute("""
            INSERT INTO sender_analysis (
                analysis_date, total_senders, network_statistics, recommendations
            ) VALUES (?, ?, ?, ?)
        """, (
            analysis.analysis_date.isoformat(),
            analysis.total_senders,
            json.dumps(analysis.network_statistics),
            json.dumps(analysis.recommendations)
        ))
        
        analysis_id = cursor.lastrowid
        
        # Insert sender profile records
        for profile in analysis.sender_profiles:
            cursor.execute("""
                INSERT INTO sender_profiles (
                    analysis_id, sender_email, sender_name, classification,
                    confidence_score, importance_score, relationship_strength,
                    metrics, trends, communication_pattern, contact_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                profile.sender_email,
                profile.sender_name,
                profile.classification,
                profile.confidence_score,
                profile.importance_score,
                profile.relationship_strength,
                json.dumps(profile.metrics, default=str),
                json.dumps(profile.trends),
                json.dumps(profile.communication_pattern),
                json.dumps(profile.contact_info)
            ))
        
        conn.commit()
        conn.close()
        
        print(f"👥 Sender analysis saved to database: {db_path}")
        print(f"   Analysis ID: {analysis_id}")


if __name__ == "__main__":
    # Test the sender analyzer
    print("🧪 Testing Sender Analytics Engine")
    
    analyzer = SenderAnalyzer()
    
    # Create test data
    test_emails_by_sender = {
        "john.doe@important-client.com": [
            {"sender_name": "John Doe", "date": "2024-01-15", "subject": "Project Discussion"},
            {"sender_name": "John Doe", "date": "2024-01-20", "subject": "Follow-up"},
            {"sender_name": "John Doe", "date": "2024-02-05", "subject": "Budget Review"},
            {"sender_name": "John Doe", "date": "2024-02-10", "subject": "Timeline Update"},
            {"sender_name": "John Doe", "date": "2024-03-01", "subject": "Milestone Reached"}
        ],
        "noreply@automated-system.com": [
            {"sender_name": "System Notification", "date": "2024-01-10", "subject": "Password Reset"},
            {"sender_name": "System Notification", "date": "2024-01-15", "subject": "Account Update"},
            {"sender_name": "System Notification", "date": "2024-01-20", "subject": "Security Alert"}
        ],
        "sales@vendor.com": [
            {"sender_name": "Sales Team", "date": "2024-01-12", "subject": "Product Demo"},
            {"sender_name": "Sales Team", "date": "2024-02-15", "subject": "Special Offer"},
        ],
        "colleague@company.com": [
            {"sender_name": "Jane Smith", "date": "2024-01-08", "subject": "Meeting Notes"},
            {"sender_name": "Jane Smith", "date": "2024-01-10", "subject": "Report Review"},
            {"sender_name": "Jane Smith", "date": "2024-01-12", "subject": "Team Update"},
            {"sender_name": "Jane Smith", "date": "2024-01-15", "subject": "Project Status"}
        ]
    }
    
    # Run analysis
    analysis = analyzer.analyze_all_senders(test_emails_by_sender)
    
    # Display results
    print(f"\n👥 Sender Analysis Results:")
    print(f"   Total senders: {analysis.total_senders}")
    print(f"   Average importance: {analysis.network_statistics['avg_importance_score']}")
    print(f"   High-value contacts: {analysis.network_statistics['high_value_contacts']}")
    
    # Show top senders
    print(f"\n🔝 Top Senders:")
    for i, (email, count) in enumerate(analysis.top_senders[:5], 1):
        profile = next(p for p in analysis.sender_profiles if p.sender_email == email)
        print(f"   {i}. {email} ({count} emails)")
        print(f"      Classification: {profile.classification} (confidence: {profile.confidence_score:.1f})")
        print(f"      Importance: {profile.importance_score:.1f}/10")
        print(f"      Pattern: {profile.communication_pattern.get('pattern_type', 'unknown')}")
    
    # Show network statistics
    print(f"\n📊 Network Statistics:")
    print(f"   Classifications: {analysis.network_statistics['classification_distribution']}")
    print(f"   Communication patterns: {analysis.network_statistics['pattern_distribution']}")
    
    # Show recommendations
    print(f"\n💡 Recommendations:")
    for rec in analysis.recommendations:
        print(f"   • {rec}")
    
    # Save analysis
    analyzer.save_analysis_to_db(analysis)
    
    print("\n✅ Sender Analytics test completed!") 