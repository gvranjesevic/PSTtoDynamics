#!/usr/bin/env python3
"""
Phase 3 Analytics Integration
============================

Integration module that connects Phase 3 analytics capabilities
with the main email import system. Provides seamless analytics
collection during import operations and comprehensive reporting.

Features:
- Automatic analytics collection during imports
- Real-time monitoring and progress tracking  
- Post-import analysis and reporting
- Integration with existing Phase 1 & 2 modules
- Comprehensive dashboard data preparation
"""

import sys
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.append('..')
from config import *

# Import Phase 3 analytics modules
from import_analytics import ImportAnalytics, get_analytics
from timeline_analyzer import TimelineAnalyzer
from sender_analytics import SenderAnalyzer

# Import Phase 1 & 2 modules
try:
    sys.path.append('..')
    from pst_reader import PSTReader
    from contact_creator import ContactCreator
    from email_comparator import EmailComparator
    from bulk_processor import BulkProcessor
    PHASE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some phase modules not available: {e}")
    PHASE_MODULES_AVAILABLE = False


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report combining all Phase 3 insights."""
    report_id: str
    generated_at: datetime
    import_session: Optional[Dict]
    timeline_analysis: Optional[Dict]
    sender_analysis: Optional[Dict]
    summary_insights: Dict[str, Any]
    recommendations: List[str]
    action_items: List[str]


class Phase3Analytics:
    """Main Phase 3 analytics orchestrator."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        
        # Initialize analytics engines
        self.import_analytics = ImportAnalytics(enabled=enabled)
        self.timeline_analyzer = TimelineAnalyzer()
        self.sender_analyzer = SenderAnalyzer()
        
        # Integration flags
        self.auto_analyze_on_import = True
        self.auto_generate_reports = True
        self.real_time_monitoring = True
        
        print("🚀 Phase 3 Analytics Integration initialized" + (" (enabled)" if enabled else " (disabled)"))
    
    def start_import_session(self, session_id: Optional[str] = None) -> str:
        """Start analytics tracking for an import session."""
        if not self.enabled:
            return "analytics_disabled"
        
        session_id = self.import_analytics.start_session(session_id)
        print(f"📊 Analytics tracking started for session: {session_id}")
        return session_id
    
    def track_pst_scanning(self, pst_path: str, total_emails: int, senders_found: Dict[str, int]):
        """Track PST scanning phase."""
        if not self.enabled:
            return
        
        self.import_analytics.set_total_emails(total_emails)
        
        print(f"📧 PST Scanning tracked:")
        print(f"   Total emails: {total_emails:,}")
        print(f"   Unique senders: {len(senders_found)}")
        print(f"   Top sender: {max(senders_found.items(), key=lambda x: x[1]) if senders_found else 'None'}")
    
    def track_batch_processing(self, batch_number: int, emails: List[Dict], 
                             results: Dict[str, int]) -> str:
        """Track individual batch processing."""
        if not self.enabled:
            return "analytics_disabled"
        
        batch_id = self.import_analytics.start_batch(batch_number, len(emails))
        
        # Track results
        success_count = results.get('successful', 0)
        error_count = results.get('failed', 0)
        duplicates = results.get('duplicates', 0)
        contacts_created = results.get('contacts_created', 0)
        
        # Record analytics events
        for _ in range(duplicates):
            self.import_analytics.record_duplicate_detected()
        
        for _ in range(contacts_created):
            self.import_analytics.record_contact_created()
        
        # Record any errors
        for error_type, count in results.get('errors', {}).items():
            for _ in range(count):
                self.import_analytics.record_error(error_type)
        
        self.import_analytics.end_batch(success_count, error_count)
        return batch_id
    
    def complete_import_session(self) -> Dict[str, Any]:
        """Complete import session and return analytics summary."""
        if not self.enabled:
            return {"analytics_enabled": False}
        
        self.import_analytics.end_session()
        
        # Get session statistics
        stats = self.import_analytics.get_current_stats()
        
        print(f"📊 Import session analytics completed")
        print(f"   Success rate: {stats.get('current_success_rate', 0):.1%}")
        print(f"   Total processed: {stats.get('processed_emails', 0):,} emails")
        print(f"   Duration: {stats.get('elapsed_time_minutes', 0):.1f} minutes")
        
        return stats
    
    def analyze_imported_data(self, emails_by_sender: Dict[str, List[Dict]], 
                            generate_report: bool = True) -> Optional[AnalyticsReport]:
        """Perform comprehensive analysis of imported email data."""
        if not self.enabled:
            return None
        
        print("🔍 Starting comprehensive post-import analysis...")
        
        # Prepare data for timeline analysis
        timeline_data = {}
        sender_data = {}
        
        for sender_email, emails in emails_by_sender.items():
            # Prepare timeline data (extract dates)
            email_dates = []
            email_data_for_sender = []
            
            for email in emails:
                # Extract date
                email_date = None
                if isinstance(email.get('date'), str):
                    try:
                        email_date = datetime.fromisoformat(email['date']).date()
                    except:
                        try:
                            email_date = datetime.strptime(email['date'], '%Y-%m-%d').date()
                        except:
                            pass
                elif hasattr(email.get('date'), 'date'):
                    email_date = email['date'].date()
                
                if email_date:
                    email_dates.append(email_date)
                
                # Prepare sender analysis data
                email_data_for_sender.append({
                    'sender_name': email.get('sender_name', ''),
                    'date': email_date.isoformat() if email_date else None,
                    'subject': email.get('subject', ''),
                    'body_preview': email.get('body', '')[:100] if email.get('body') else ''
                })
            
            timeline_data[sender_email] = email_dates
            sender_data[sender_email] = email_data_for_sender
        
        # Run timeline analysis
        print("📈 Analyzing timeline completeness...")
        timeline_analysis = self.timeline_analyzer.analyze_multiple_contacts(timeline_data)
        
        # Run sender analysis  
        print("👥 Analyzing sender patterns...")
        sender_analysis = self.sender_analyzer.analyze_all_senders(sender_data)
        
        # Generate comprehensive report
        if generate_report:
            report = self._generate_comprehensive_report(timeline_analysis, sender_analysis)
            return report
        
        return None
    
    def _generate_comprehensive_report(self, timeline_analysis, sender_analysis) -> AnalyticsReport:
        """Generate comprehensive analytics report."""
        report_id = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get current import session data
        import_session_data = self.import_analytics.get_current_stats()
        
        # Generate summary insights
        summary_insights = {
            "import_performance": {
                "total_emails_processed": import_session_data.get('processed_emails', 0),
                "success_rate": import_session_data.get('current_success_rate', 0),
                "processing_speed": f"{import_session_data.get('processed_emails', 0) / max(import_session_data.get('elapsed_time_minutes', 1), 1):.0f} emails/min",
                "duplicates_found": import_session_data.get('duplicates_detected', 0),
                "contacts_created": import_session_data.get('contacts_created', 0)
            },
            "timeline_insights": {
                "overall_completeness": f"{timeline_analysis.overall_completeness:.1f}%",
                "contacts_analyzed": timeline_analysis.contacts_analyzed,
                "critical_gaps": timeline_analysis.summary_stats.get('critical_gaps', 0),
                "high_completeness_contacts": timeline_analysis.summary_stats.get('contacts_with_high_completeness', 0)
            },
            "sender_insights": {
                "total_senders": sender_analysis.total_senders,
                "high_value_contacts": sender_analysis.network_statistics.get('high_value_contacts', 0),
                "avg_importance_score": sender_analysis.network_statistics.get('avg_importance_score', 0),
                "active_contacts": sender_analysis.network_statistics.get('active_contacts', 0),
                "automated_senders": sender_analysis.network_statistics.get('classification_distribution', {}).get('automated', 0)
            }
        }
        
        # Combine recommendations from all analyses
        all_recommendations = []
        all_recommendations.extend(timeline_analysis.recommendations)
        all_recommendations.extend(sender_analysis.recommendations)
        
        # Generate action items
        action_items = self._generate_action_items(summary_insights, timeline_analysis, sender_analysis)
        
        report = AnalyticsReport(
            report_id=report_id,
            generated_at=datetime.now(),
            import_session=import_session_data,
            timeline_analysis=asdict(timeline_analysis),
            sender_analysis=asdict(sender_analysis),
            summary_insights=summary_insights,
            recommendations=all_recommendations,
            action_items=action_items
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _generate_action_items(self, insights: Dict, timeline_analysis, sender_analysis) -> List[str]:
        """Generate specific action items based on analysis."""
        actions = []
        
        # Import performance actions
        success_rate = insights['import_performance']['success_rate']
        if success_rate < 0.95:
            actions.append(f"Investigate import failures (success rate: {success_rate:.1%})")
        
        duplicates = insights['import_performance']['duplicates_found']
        if duplicates > insights['import_performance']['total_emails_processed'] * 0.1:
            actions.append(f"Review duplicate detection - {duplicates} duplicates found")
        
        # Timeline actions
        completeness = float(insights['timeline_insights']['overall_completeness'].rstrip('%'))
        if completeness < 80:
            actions.append("Investigate timeline gaps - completeness below 80%")
        
        critical_gaps = insights['timeline_insights']['critical_gaps']
        if critical_gaps > 0:
            actions.append(f"Review {critical_gaps} critical timeline gaps")
        
        # Sender actions
        high_value = insights['sender_insights']['high_value_contacts']
        if high_value > 0:
            actions.append(f"Ensure complete timeline coverage for {high_value} high-value contacts")
        
        automated = insights['sender_insights']['automated_senders']
        total_senders = insights['sender_insights']['total_senders']
        if automated > total_senders * 0.3:
            actions.append(f"Consider filtering {automated} automated senders in future imports")
        
        return actions
    
    def _save_report(self, report: AnalyticsReport):
        """Save comprehensive report to files and database."""
        # Ensure reports directory exists
        reports_dir = "Phase3_Analytics/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save JSON report
        json_path = f"{reports_dir}/{report.report_id}.json"
        with open(json_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save summary text report
        text_path = f"{reports_dir}/{report.report_id}_summary.txt"
        with open(text_path, 'w') as f:
            f.write(self._format_text_report(report))
        
        print(f"📊 Comprehensive report saved:")
        print(f"   JSON: {json_path}")
        print(f"   Summary: {text_path}")
    
    def _format_text_report(self, report: AnalyticsReport) -> str:
        """Format report as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append("PHASE 3 ANALYTICS COMPREHENSIVE REPORT")
        lines.append("=" * 80)
        lines.append(f"Report ID: {report.report_id}")
        lines.append(f"Generated: {report.generated_at}")
        lines.append("")
        
        # Import Performance
        lines.append("IMPORT PERFORMANCE")
        lines.append("-" * 40)
        perf = report.summary_insights['import_performance']
        lines.append(f"Total Emails Processed: {perf['total_emails_processed']:,}")
        lines.append(f"Success Rate: {perf['success_rate']:.1%}")
        lines.append(f"Processing Speed: {perf['processing_speed']}")
        lines.append(f"Duplicates Found: {perf['duplicates_found']:,}")
        lines.append(f"Contacts Created: {perf['contacts_created']:,}")
        lines.append("")
        
        # Timeline Analysis
        lines.append("TIMELINE ANALYSIS")
        lines.append("-" * 40)
        timeline = report.summary_insights['timeline_insights']
        lines.append(f"Overall Completeness: {timeline['overall_completeness']}")
        lines.append(f"Contacts Analyzed: {timeline['contacts_analyzed']:,}")
        lines.append(f"Critical Gaps: {timeline['critical_gaps']}")
        lines.append(f"High Completeness Contacts: {timeline['high_completeness_contacts']}")
        lines.append("")
        
        # Sender Analysis
        lines.append("SENDER ANALYSIS")
        lines.append("-" * 40)
        sender = report.summary_insights['sender_insights']
        lines.append(f"Total Senders: {sender['total_senders']:,}")
        lines.append(f"High-Value Contacts: {sender['high_value_contacts']}")
        lines.append(f"Average Importance Score: {sender['avg_importance_score']:.1f}/10")
        lines.append(f"Active Contacts: {sender['active_contacts']}")
        lines.append(f"Automated Senders: {sender['automated_senders']}")
        lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 40)
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Action Items
        if report.action_items:
            lines.append("ACTION ITEMS")
            lines.append("-" * 40)
            for i, action in enumerate(report.action_items, 1):
                lines.append(f"{i}. {action}")
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time data for analytics dashboard."""
        if not self.enabled:
            return {"analytics_enabled": False}
        
        current_stats = self.import_analytics.get_current_stats()
        performance_summary = self.import_analytics.get_performance_summary()
        
        dashboard_data = {
            "analytics_enabled": True,
            "last_updated": datetime.now().isoformat(),
            "current_session": current_stats,
            "performance_summary": performance_summary,
            "system_status": "active" if current_stats.get('session_id') else "idle"
        }
        
        return dashboard_data
    
    def export_all_analytics(self, format_type: str = "json") -> Dict[str, str]:
        """Export all analytics data in specified format."""
        if not self.enabled:
            return {"error": "Analytics disabled"}
        
        exports = {}
        
        # Export import analytics
        exports['import_analytics'] = self.import_analytics.export_analytics(format_type)
        
        # Get recent analyses from databases if available
        try:
            # Timeline analysis export would go here
            exports['timeline_analysis'] = "Timeline analysis export would be implemented"
            
            # Sender analysis export would go here  
            exports['sender_analysis'] = "Sender analysis export would be implemented"
        except Exception as e:
            exports['export_note'] = f"Some exports unavailable: {e}"
        
        return exports


# Global Phase 3 analytics instance
phase3_analytics = Phase3Analytics(enabled=getattr(FeatureFlags, 'IMPORT_ANALYTICS', False))


def get_phase3_analytics() -> Phase3Analytics:
    """Get the global Phase 3 analytics instance."""
    return phase3_analytics


if __name__ == "__main__":
    # Test Phase 3 integration
    print("🧪 Testing Phase 3 Analytics Integration")
    
    # Create test instance
    test_analytics = Phase3Analytics(enabled=True)
    
    # Simulate import session
    session_id = test_analytics.start_import_session()
    
    # Simulate PST scanning
    test_senders = {
        "john.doe@client.com": 25,
        "jane.smith@vendor.com": 15,
        "noreply@system.com": 50,
        "colleague@company.com": 30
    }
    test_analytics.track_pst_scanning("test.pst", 120, test_senders)
    
    # Simulate batch processing
    for batch_num in range(1, 4):
        results = {
            'successful': 35,
            'failed': 5,
            'duplicates': 3,
            'contacts_created': 2,
            'errors': {'network_timeout': 2, 'validation_error': 3}
        }
        test_analytics.track_batch_processing(batch_num, [{}] * 40, results)
    
    # Complete session
    final_stats = test_analytics.complete_import_session()
    
    # Simulate comprehensive analysis
    test_email_data = {
        "john.doe@client.com": [
            {"sender_name": "John Doe", "date": "2024-01-15", "subject": "Project Update"},
            {"sender_name": "John Doe", "date": "2024-02-01", "subject": "Review"},
            {"sender_name": "John Doe", "date": "2024-03-15", "subject": "Final Report"}
        ],
        "jane.smith@vendor.com": [
            {"sender_name": "Jane Smith", "date": "2024-01-10", "subject": "Quote"},
            {"sender_name": "Jane Smith", "date": "2024-02-20", "subject": "Invoice"}
        ]
    }
    
    report = test_analytics.analyze_imported_data(test_email_data)
    
    # Display results
    print(f"\n📊 Integration Test Results:")
    print(f"   Session completed: {session_id}")
    print(f"   Final stats: {final_stats}")
    if report:
        print(f"   Report generated: {report.report_id}")
        print(f"   Action items: {len(report.action_items)}")
    
    # Test dashboard data
    dashboard_data = test_analytics.get_real_time_dashboard_data()
    print(f"\n📈 Dashboard data available: {dashboard_data['analytics_enabled']}")
    
    print("\n✅ Phase 3 Analytics Integration test completed!") 