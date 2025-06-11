#!/usr/bin/env python3
"""
Timeline Analyzer
=================

Phase 3.2 - Timeline completeness analysis and gap detection.
Identifies missing emails, analyzes coverage patterns, and provides
recommendations for improving timeline completeness.

Features:
- Email coverage analysis by date ranges
- Intelligent gap detection with context awareness
- Timeline completeness scoring (0-100%)
- Pattern recognition for normal vs. abnormal gaps
- Recommendation engine for missing data
- Multi-contact timeline analysis
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import calendar
import statistics

# Add parent directory to path for imports
sys.path.append('..')
from config import *

# Try to import holidays for better gap analysis
try:
    import holidays
    HOLIDAYS_AVAILABLE = True
    us_holidays = holidays.US()
except ImportError:
    HOLIDAYS_AVAILABLE = False
    print("⚠️ holidays library not available - holiday gap detection disabled")


@dataclass
class TimelineGap:
    """Represents a gap in email timeline."""
    contact_email: str
    contact_id: Optional[str]
    start_date: date
    end_date: date
    gap_days: int
    severity: str  # 'minor', 'moderate', 'major', 'critical'
    gap_type: str  # 'weekend', 'holiday', 'vacation', 'suspicious', 'unknown'
    context: Dict[str, Any]
    suggested_action: str


@dataclass
class ContactTimeline:
    """Complete timeline analysis for a contact."""
    contact_email: str
    contact_id: Optional[str]
    first_email: date
    last_email: date
    total_timeline_days: int
    email_count: int
    coverage_days: int
    completeness_score: float
    gaps: List[TimelineGap]
    email_frequency: Dict[str, int]  # monthly frequency
    communication_pattern: Dict[str, Any]


@dataclass
class TimelineAnalysis:
    """Complete timeline analysis results."""
    analysis_date: datetime
    total_contacts: int
    contacts_analyzed: int
    overall_completeness: float
    contact_timelines: List[ContactTimeline]
    summary_stats: Dict[str, Any]
    recommendations: List[str]


class TimelineAnalyzer:
    """Analyzes email timelines to identify gaps and completeness."""
    
    def __init__(self, dynamics_data_module=None):
        self.dynamics_data = dynamics_data_module
        self.gap_thresholds = {
            'minor': 7,      # 1 week
            'moderate': 14,  # 2 weeks  
            'major': 30,     # 1 month
            'critical': 90   # 3 months
        }
        
        # Pattern recognition thresholds
        self.min_emails_for_pattern = 10
        self.vacation_gap_threshold = 14  # days
        self.suspicious_gap_threshold = 21  # days
        
        print("📈 Timeline Analyzer initialized")
    
    def _classify_gap_severity(self, gap_days: int) -> str:
        """Classify gap severity based on duration."""
        if gap_days <= self.gap_thresholds['minor']:
            return 'minor'
        elif gap_days <= self.gap_thresholds['moderate']:
            return 'moderate'
        elif gap_days <= self.gap_thresholds['major']:
            return 'major'
        else:
            return 'critical'
    
    def _classify_gap_type(self, start_date: date, end_date: date, email_frequency: Dict) -> str:
        """Classify the type of gap based on context."""
        gap_days = (end_date - start_date).days
        
        # Check if it's mostly weekends
        weekend_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_days += 1
            current_date += timedelta(days=1)
        
        weekend_ratio = weekend_days / gap_days if gap_days > 0 else 0
        
        # Check for holidays if available
        holiday_days = 0
        if HOLIDAYS_AVAILABLE:
            current_date = start_date
            while current_date <= end_date:
                if current_date in us_holidays:
                    holiday_days += 1
                current_date += timedelta(days=1)
        
        # Classification logic
        if weekend_ratio > 0.8:
            return 'weekend'
        elif holiday_days > 0 and gap_days <= 10:
            return 'holiday'
        elif gap_days >= self.vacation_gap_threshold and gap_days <= 21:
            return 'vacation'
        elif gap_days >= self.suspicious_gap_threshold:
            return 'suspicious'
        else:
            return 'unknown'
    
    def _calculate_email_frequency(self, email_dates: List[date]) -> Dict[str, int]:
        """Calculate monthly email frequency patterns."""
        monthly_counts = defaultdict(int)
        
        for email_date in email_dates:
            month_key = email_date.strftime('%Y-%m')
            monthly_counts[month_key] += 1
        
        return dict(monthly_counts)
    
    def _detect_communication_pattern(self, email_dates: List[date]) -> Dict[str, Any]:
        """Analyze communication patterns."""
        if len(email_dates) < self.min_emails_for_pattern:
            return {'pattern_detected': False, 'reason': 'insufficient_data'}
        
        # Sort dates
        sorted_dates = sorted(email_dates)
        
        # Calculate intervals between emails
        intervals = []
        for i in range(1, len(sorted_dates)):
            interval = (sorted_dates[i] - sorted_dates[i-1]).days
            intervals.append(interval)
        
        if not intervals:
            return {'pattern_detected': False, 'reason': 'single_email'}
        
        # Calculate statistics
        avg_interval = statistics.mean(intervals)
        median_interval = statistics.median(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Day of week analysis
        day_counts = defaultdict(int)
        for email_date in email_dates:
            day_counts[email_date.weekday()] += 1
        
        most_common_day = max(day_counts, key=day_counts.get)
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'pattern_detected': True,
            'avg_interval_days': round(avg_interval, 1),
            'median_interval_days': median_interval,
            'interval_consistency': round(1 - (std_interval / avg_interval) if avg_interval > 0 else 0, 2),
            'most_common_day': day_names[most_common_day],
            'weekend_emails': day_counts[5] + day_counts[6],
            'weekday_emails': sum(day_counts[i] for i in range(5)),
            'total_span_days': (sorted_dates[-1] - sorted_dates[0]).days,
            'communication_frequency': 'high' if avg_interval < 7 else 'medium' if avg_interval < 30 else 'low'
        }
    
    def _find_timeline_gaps(self, email_dates: List[date], contact_email: str) -> List[TimelineGap]:
        """Identify gaps in the email timeline."""
        if len(email_dates) < 2:
            return []
        
        sorted_dates = sorted(email_dates)
        gaps = []
        email_frequency = self._calculate_email_frequency(email_dates)
        
        for i in range(1, len(sorted_dates)):
            gap_start = sorted_dates[i-1] + timedelta(days=1)
            gap_end = sorted_dates[i] - timedelta(days=1)
            gap_days = (gap_end - gap_start).days + 1
            
            # Only consider significant gaps
            if gap_days >= 2:  # More than 1 day gap
                severity = self._classify_gap_severity(gap_days)
                gap_type = self._classify_gap_type(gap_start, gap_end, email_frequency)
                
                # Generate context and suggestions
                context = {
                    'before_gap_emails': sum(1 for d in sorted_dates if d < gap_start),
                    'after_gap_emails': sum(1 for d in sorted_dates if d > gap_end),
                    'gap_percentage': (gap_days / (sorted_dates[-1] - sorted_dates[0]).days) * 100
                }
                
                suggested_action = self._generate_gap_suggestion(gap_type, severity, gap_days)
                
                gap = TimelineGap(
                    contact_email=contact_email,
                    contact_id=None,  # Will be filled if available
                    start_date=gap_start,
                    end_date=gap_end,
                    gap_days=gap_days,
                    severity=severity,
                    gap_type=gap_type,
                    context=context,
                    suggested_action=suggested_action
                )
                
                gaps.append(gap)
        
        return gaps
    
    def _generate_gap_suggestion(self, gap_type: str, severity: str, gap_days: int) -> str:
        """Generate appropriate suggestion for gap resolution."""
        if gap_type == 'weekend':
            return "Normal weekend gap - no action needed"
        elif gap_type == 'holiday':
            return "Holiday period gap - expected behavior"
        elif gap_type == 'vacation':
            return "Possible vacation period - check for out-of-office emails"
        elif gap_type == 'suspicious' and severity in ['major', 'critical']:
            return f"Significant {gap_days}-day gap - check additional PST files or email archives"
        elif severity == 'critical':
            return f"Critical {gap_days}-day gap - verify data sources and check for missing archives"
        elif severity == 'major':
            return f"Major {gap_days}-day gap - review import logs and consider additional data sources"
        else:
            return f"Review {gap_days}-day gap for completeness"
    
    def _calculate_completeness_score(self, total_days: int, gaps: List[TimelineGap]) -> float:
        """Calculate timeline completeness score (0-100)."""
        if total_days == 0:
            return 0.0
        
        # Calculate gap penalty based on severity
        gap_penalty = 0
        for gap in gaps:
            if gap.gap_type in ['weekend', 'holiday']:
                penalty = gap.gap_days * 0.1  # Minimal penalty for expected gaps
            elif gap.severity == 'minor':
                penalty = gap.gap_days * 0.5
            elif gap.severity == 'moderate':
                penalty = gap.gap_days * 1.0
            elif gap.severity == 'major':
                penalty = gap.gap_days * 2.0
            else:  # critical
                penalty = gap.gap_days * 3.0
            
            gap_penalty += penalty
        
        # Calculate score
        max_penalty = total_days * 3.0  # Maximum possible penalty
        score = max(0, 100 - (gap_penalty / max_penalty * 100))
        
        return round(score, 1)
    
    def analyze_contact_timeline(self, contact_email: str, email_dates: List[date]) -> ContactTimeline:
        """Analyze timeline for a single contact."""
        if not email_dates:
            return ContactTimeline(
                contact_email=contact_email,
                contact_id=None,
                first_email=date.today(),
                last_email=date.today(),
                total_timeline_days=0,
                email_count=0,
                coverage_days=0,
                completeness_score=0.0,
                gaps=[],
                email_frequency={},
                communication_pattern={'pattern_detected': False}
            )
        
        sorted_dates = sorted(set(email_dates))  # Remove duplicates and sort
        first_email = sorted_dates[0]
        last_email = sorted_dates[-1]
        total_days = (last_email - first_email).days + 1
        coverage_days = len(sorted_dates)
        
        # Find gaps
        gaps = self._find_timeline_gaps(sorted_dates, contact_email)
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(total_days, gaps)
        
        # Analyze patterns
        email_frequency = self._calculate_email_frequency(sorted_dates)
        communication_pattern = self._detect_communication_pattern(sorted_dates)
        
        return ContactTimeline(
            contact_email=contact_email,
            contact_id=None,  # Can be filled from Dynamics data
            first_email=first_email,
            last_email=last_email,
            total_timeline_days=total_days,
            email_count=len(email_dates),
            coverage_days=coverage_days,
            completeness_score=completeness_score,
            gaps=gaps,
            email_frequency=email_frequency,
            communication_pattern=communication_pattern
        )
    
    def analyze_multiple_contacts(self, contacts_data: Dict[str, List[date]]) -> TimelineAnalysis:
        """Analyze timelines for multiple contacts."""
        print(f"📈 Analyzing timelines for {len(contacts_data)} contacts...")
        
        contact_timelines = []
        completeness_scores = []
        total_gaps = 0
        critical_gaps = 0
        
        for contact_email, email_dates in contacts_data.items():
            timeline = self.analyze_contact_timeline(contact_email, email_dates)
            contact_timelines.append(timeline)
            
            if timeline.completeness_score > 0:
                completeness_scores.append(timeline.completeness_score)
            
            total_gaps += len(timeline.gaps)
            critical_gaps += len([g for g in timeline.gaps if g.severity == 'critical'])
        
        # Calculate overall statistics
        overall_completeness = statistics.mean(completeness_scores) if completeness_scores else 0
        
        summary_stats = {
            'total_contacts_analyzed': len(contacts_data),
            'contacts_with_emails': len([t for t in contact_timelines if t.email_count > 0]),
            'overall_completeness_score': round(overall_completeness, 1),
            'total_gaps_found': total_gaps,
            'critical_gaps': critical_gaps,
            'avg_emails_per_contact': round(statistics.mean([t.email_count for t in contact_timelines]), 1),
            'contacts_with_high_completeness': len([t for t in contact_timelines if t.completeness_score >= 90]),
            'contacts_needing_attention': len([t for t in contact_timelines if t.completeness_score < 70])
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(contact_timelines, summary_stats)
        
        return TimelineAnalysis(
            analysis_date=datetime.now(),
            total_contacts=len(contacts_data),
            contacts_analyzed=len(contact_timelines),
            overall_completeness=overall_completeness,
            contact_timelines=contact_timelines,
            summary_stats=summary_stats,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, timelines: List[ContactTimeline], stats: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Overall completeness recommendations
        if stats['overall_completeness_score'] < 70:
            recommendations.append("Overall timeline completeness is below 70% - consider importing additional PST files or email archives")
        
        # Critical gaps recommendations
        if stats['critical_gaps'] > 0:
            recommendations.append(f"Found {stats['critical_gaps']} critical gaps - review these high-priority missing periods")
        
        # Low-activity contacts
        low_activity = [t for t in timelines if t.email_count < 5 and t.total_timeline_days > 30]
        if len(low_activity) > stats['total_contacts_analyzed'] * 0.2:
            recommendations.append(f"{len(low_activity)} contacts have very low email activity - verify these are important contacts")
        
        # Contacts needing attention
        if stats['contacts_needing_attention'] > 0:
            recommendations.append(f"{stats['contacts_needing_attention']} contacts need attention due to low completeness scores")
        
        # Specific contact recommendations
        suspicious_contacts = [t for t in timelines if len([g for g in t.gaps if g.gap_type == 'suspicious']) > 0]
        if suspicious_contacts:
            recommendations.append(f"{len(suspicious_contacts)} contacts have suspicious gaps that may indicate missing data")
        
        return recommendations
    
    def export_analysis(self, analysis: TimelineAnalysis, format_type: str = "json") -> str:
        """Export timeline analysis in specified format."""
        if format_type.lower() == "json":
            return json.dumps(asdict(analysis), indent=2, default=str)
        elif format_type.lower() == "csv":
            return self._export_to_csv(analysis)
        else:
            return str(asdict(analysis))
    
    def _export_to_csv(self, analysis: TimelineAnalysis) -> str:
        """Export analysis results to CSV format."""
        lines = []
        lines.append("Contact Email,Contact ID,First Email,Last Email,Timeline Days,Email Count,Coverage Days,Completeness Score,Gap Count,Critical Gaps")
        
        for timeline in analysis.contact_timelines:
            critical_gaps = len([g for g in timeline.gaps if g.severity == 'critical'])
            line = f"{timeline.contact_email},{timeline.contact_id or ''},{timeline.first_email},{timeline.last_email},{timeline.total_timeline_days},{timeline.email_count},{timeline.coverage_days},{timeline.completeness_score},{len(timeline.gaps)},{critical_gaps}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def save_analysis_to_db(self, analysis: TimelineAnalysis, db_path: str = "Phase3_Analytics/timeline_analysis.db"):
        """Save analysis results to database."""
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TEXT NOT NULL,
                total_contacts INTEGER,
                overall_completeness REAL,
                summary_stats TEXT,
                recommendations TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_timelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                contact_email TEXT NOT NULL,
                contact_id TEXT,
                first_email TEXT,
                last_email TEXT,
                total_timeline_days INTEGER,
                email_count INTEGER,
                coverage_days INTEGER,
                completeness_score REAL,
                gaps_data TEXT,
                email_frequency TEXT,
                communication_pattern TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES timeline_analysis (id)
            )
        """)
        
        # Insert analysis record
        cursor.execute("""
            INSERT INTO timeline_analysis (
                analysis_date, total_contacts, overall_completeness,
                summary_stats, recommendations
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            analysis.analysis_date.isoformat(),
            analysis.total_contacts,
            analysis.overall_completeness,
            json.dumps(analysis.summary_stats),
            json.dumps(analysis.recommendations)
        ))
        
        analysis_id = cursor.lastrowid
        
        # Insert contact timeline records
        for timeline in analysis.contact_timelines:
            cursor.execute("""
                INSERT INTO contact_timelines (
                    analysis_id, contact_email, contact_id, first_email, last_email,
                    total_timeline_days, email_count, coverage_days, completeness_score,
                    gaps_data, email_frequency, communication_pattern
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                timeline.contact_email,
                timeline.contact_id,
                timeline.first_email.isoformat(),
                timeline.last_email.isoformat(),
                timeline.total_timeline_days,
                timeline.email_count,
                timeline.coverage_days,
                timeline.completeness_score,
                json.dumps([asdict(gap) for gap in timeline.gaps], default=str),
                json.dumps(timeline.email_frequency),
                json.dumps(timeline.communication_pattern)
            ))
        
        conn.commit()
        conn.close()
        
        print(f"📊 Timeline analysis saved to database: {db_path}")
        print(f"   Analysis ID: {analysis_id}")


if __name__ == "__main__":
    # Test the timeline analyzer
    print("🧪 Testing Timeline Analyzer")
    
    analyzer = TimelineAnalyzer()
    
    # Create test data
    test_contacts = {
        "john.doe@example.com": [
            date(2024, 1, 15),
            date(2024, 1, 20),
            date(2024, 2, 5),
            date(2024, 2, 10),
            date(2024, 3, 1),  # 19-day gap here
            date(2024, 3, 25),
            date(2024, 4, 10),
            date(2024, 5, 15),  # 35-day gap here
            date(2024, 6, 1)
        ],
        "jane.smith@company.com": [
            date(2024, 1, 10),
            date(2024, 1, 12),
            date(2024, 1, 14),
            date(2024, 1, 16),
            date(2024, 1, 18),
            date(2024, 1, 22),
            date(2024, 1, 24),
            date(2024, 1, 26)
        ]
    }
    
    # Run analysis
    analysis = analyzer.analyze_multiple_contacts(test_contacts)
    
    # Display results
    print(f"\n📈 Analysis Results:")
    print(f"   Total contacts: {analysis.total_contacts}")
    print(f"   Overall completeness: {analysis.overall_completeness:.1f}%")
    print(f"   Critical gaps found: {analysis.summary_stats['critical_gaps']}")
    
    # Show contact details
    for timeline in analysis.contact_timelines:
        print(f"\n👤 {timeline.contact_email}:")
        print(f"   Completeness: {timeline.completeness_score:.1f}%")
        print(f"   Email count: {timeline.email_count}")
        print(f"   Timeline: {timeline.first_email} to {timeline.last_email}")
        print(f"   Gaps found: {len(timeline.gaps)}")
        
        for gap in timeline.gaps[:3]:  # Show first 3 gaps
            print(f"      {gap.severity} {gap.gap_type} gap: {gap.gap_days} days ({gap.start_date} to {gap.end_date})")
    
    # Show recommendations
    print(f"\n💡 Recommendations:")
    for rec in analysis.recommendations:
        print(f"   • {rec}")
    
    # Save analysis
    analyzer.save_analysis_to_db(analysis)
    
    print("\n✅ Timeline Analyzer test completed!") 