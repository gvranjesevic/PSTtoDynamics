"""
Email Import Engine
==================

Main orchestrator for importing emails from PST to Dynamics 365.
Now enhanced with Phase 3 Analytics for comprehensive import tracking and analysis.
"""

from typing import Dict, List, Optional, Tuple
import config
import pst_reader
import dynamics_data
from datetime import datetime

# Phase 3 Analytics Integration
try:
    import sys
    import os
    phase3_path = os.path.join(os.path.dirname(__file__), 'Phase3_Analytics')
    if phase3_path not in sys.path:
        sys.path.append(phase3_path)
    from Phase3_Analytics.phase3_integration import get_phase3_analytics
    PHASE3_AVAILABLE = True
    print("✅ Phase 3 Analytics enabled")
except ImportError as e:
    PHASE3_AVAILABLE = False
    print(f"⚠️ Phase 3 Analytics not available: {e}")


class EmailImporter:
    """Main email import engine."""
    
    def __init__(self):
        self.pst_reader = None
        self.dynamics_data = dynamics_data.get_dynamics_data()
        self.import_stats = {
            'total_senders': 0,
            'processed_senders': 0,
            'total_emails_found': 0,
            'emails_imported': 0,
            'emails_skipped_duplicate': 0,
            'emails_skipped_no_contact': 0,
            'emails_failed': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Phase 3 Analytics Integration
        self.analytics = get_phase3_analytics() if PHASE3_AVAILABLE else None
        self.current_session_id = None
    
    def get_pst_emails(self, pst_path: str = None) -> Dict[str, List[Dict]]:
        """
        Retrieves all emails from PST file grouped by sender.
        
        Args:
            pst_path: Optional PST file path
            
        Returns:
            Dictionary of emails grouped by sender email address
        """
        print("📧 Reading emails from PST file...")
        self.import_stats['start_time'] = datetime.now()
        
        emails_by_sender = pst_reader.scan_pst_file(pst_path)
        
        self.import_stats['total_senders'] = len(emails_by_sender)
        self.import_stats['total_emails_found'] = sum(len(emails) for emails in emails_by_sender.values())
        
        # Track PST scanning with Phase 3 Analytics
        if self.analytics:
            sender_counts = {sender: len(emails) for sender, emails in emails_by_sender.items()}
            self.analytics.track_pst_scanning(pst_path or config.CURRENT_PST_PATH, 
                                            self.import_stats['total_emails_found'], 
                                            sender_counts)
        
        print(f"✅ PST scan complete:")
        print(f"   📧 Total emails: {self.import_stats['total_emails_found']}")
        print(f"   👥 Unique senders: {self.import_stats['total_senders']}")
        
        return emails_by_sender
    
    def find_contact_for_sender(self, sender_email: str) -> Optional[Dict]:
        """
        Finds a Dynamics 365 contact for a sender email address.
        
        Args:
            sender_email: Email address to search for
            
        Returns:
            Contact data or None if not found
        """
        return self.dynamics_data.get_contact_by_email(sender_email)
    
    def import_emails_for_sender(self, sender_email: str, emails: List[Dict], test_mode: bool = True) -> Dict:
        """
        Imports emails for a specific sender.
        
        Args:
            sender_email: Sender email address
            emails: List of email data
            test_mode: If True, limit to first few emails
            
        Returns:
            Dictionary with import results
        """
        print(f"\n👤 Processing emails for: {sender_email}")
        
        # Find contact
        contact = self.find_contact_for_sender(sender_email)
        if not contact:
            print(f"   ❌ No contact found for {sender_email}")
            self.import_stats['emails_skipped_no_contact'] += len(emails)
            return {
                'success': False,
                'reason': 'no_contact',
                'emails_processed': 0,
                'emails_imported': 0
            }
        
        contact_id = contact['contactid']
        contact_name = contact.get('fullname', 'Unknown')
        print(f"   ✅ Found contact: {contact_name} ({contact_id})")
        
        # Get existing emails for duplicate detection
        print(f"   🔍 Checking for existing emails...")
        existing_emails = self.dynamics_data.get_emails_for_contact(contact_id)
        
        # Limit emails in test mode
        emails_to_process = emails
        if test_mode and len(emails) > config.BATCH_SIZE:
            emails_to_process = emails[:config.BATCH_SIZE]
            print(f"   🧪 Test mode: Processing only {len(emails_to_process)} of {len(emails)} emails")
        
        imported_count = 0
        skipped_count = 0
        failed_count = 0
        
        for i, email_data in enumerate(emails_to_process):
            try:
                # Check for duplicates
                if self.dynamics_data.is_email_duplicate(email_data, existing_emails):
                    print(f"   ⏭️  Skipping duplicate: {email_data.get('subject', 'No Subject')[:50]}...")
                    skipped_count += 1
                    self.import_stats['emails_skipped_duplicate'] += 1
                    continue
                
                # Import email
                email_id = self.dynamics_data.create_email(email_data, contact_id)
                
                if email_id:
                    # Update status to Closed if configured
                    if config.DEFAULT_EMAIL_STATUS.lower() == "closed":
                        self.dynamics_data.update_email_status(email_id, "Closed")
                    
                    imported_count += 1
                    self.import_stats['emails_imported'] += 1
                    
                    if imported_count % 10 == 0:
                        print(f"   📧 Imported {imported_count} emails so far...")
                else:
                    failed_count += 1
                    self.import_stats['emails_failed'] += 1
                    
            except Exception as e:
                print(f"   ❌ Error importing email: {e}")
                failed_count += 1
                self.import_stats['emails_failed'] += 1
        
        print(f"   ✅ Sender complete: {imported_count} imported, {skipped_count} skipped, {failed_count} failed")
        
        return {
            'success': True,
            'emails_processed': len(emails_to_process),
            'emails_imported': imported_count,
            'emails_skipped': skipped_count,
            'emails_failed': failed_count
        }
    
    def import_all_emails(self, pst_path: str = None, test_mode: bool = None, specific_sender: str = None) -> Dict:
        """
        Imports all emails from PST to Dynamics 365.
        
        Args:
            pst_path: Optional PST file path
            test_mode: Test mode flag (uses config default if None)
            specific_sender: Import only for this sender email
            
        Returns:
            Dictionary with overall import results
        """
        if test_mode is None:
            test_mode = config.TEST_MODE_DEFAULT
        
        print("🚀 Starting Email Import Process")
        print("=" * 50)
        
        # Start Phase 3 Analytics session
        if self.analytics:
            self.current_session_id = self.analytics.start_import_session()
        
        if test_mode:
            print("🧪 Running in TEST MODE - Limited processing")
        
        # Get emails from PST
        emails_by_sender = self.get_pst_emails(pst_path)
        
        if not emails_by_sender:
            print("❌ No emails found in PST file")
            return {'success': False, 'reason': 'no_emails'}
        
        # Filter to specific sender if requested
        if specific_sender:
            if specific_sender in emails_by_sender:
                emails_by_sender = {specific_sender: emails_by_sender[specific_sender]}
                print(f"🎯 Filtering to specific sender: {specific_sender}")
            else:
                print(f"❌ Sender not found in PST: {specific_sender}")
                return {'success': False, 'reason': 'sender_not_found'}
        
        # Process each sender
        sender_results = {}
        for sender_email, emails in emails_by_sender.items():
            try:
                result = self.import_emails_for_sender(sender_email, emails, test_mode)
                sender_results[sender_email] = result
                self.import_stats['processed_senders'] += 1
                
                # Stop in test mode after processing a few senders
                if test_mode and self.import_stats['processed_senders'] >= 3:
                    print("\n🧪 Test mode: Stopping after processing 3 senders")
                    break
                    
            except Exception as e:
                print(f"❌ Error processing sender {sender_email}: {e}")
                sender_results[sender_email] = {
                    'success': False,
                    'reason': 'processing_error',
                    'error': str(e)
                }
        
        self.import_stats['end_time'] = datetime.now()
        
        # Complete Phase 3 Analytics session
        analytics_report = None
        if self.analytics:
            final_stats = self.analytics.complete_import_session()
            
            # Run comprehensive post-import analysis
            if config.FeatureFlags.IMPORT_ANALYTICS:
                print("\n🔍 Running comprehensive post-import analysis...")
                analytics_report = self.analytics.analyze_imported_data(emails_by_sender)
        
        # Print final summary
        self._print_import_summary(sender_results, analytics_report)
        
        return {
            'success': True,
            'stats': self.import_stats,
            'sender_results': sender_results,
            'analytics_report': analytics_report
        }
    
    def _print_import_summary(self, sender_results: Dict, analytics_report=None):
        """Prints a summary of the import process."""
        print("\n" + "=" * 50)
        print("📊 IMPORT SUMMARY")
        print("=" * 50)
        
        duration = None
        if self.import_stats['start_time'] and self.import_stats['end_time']:
            duration = self.import_stats['end_time'] - self.import_stats['start_time']
        
        print(f"⏱️  Duration: {duration}")
        print(f"👥 Senders processed: {self.import_stats['processed_senders']}/{self.import_stats['total_senders']}")
        print(f"📧 Total emails found: {self.import_stats['total_emails_found']}")
        print(f"✅ Emails imported: {self.import_stats['emails_imported']}")
        print(f"⏭️  Emails skipped (duplicates): {self.import_stats['emails_skipped_duplicate']}")
        print(f"👤 Emails skipped (no contact): {self.import_stats['emails_skipped_no_contact']}")
        print(f"❌ Emails failed: {self.import_stats['emails_failed']}")
        
        # Show successful senders
        successful_senders = [email for email, result in sender_results.items() if result.get('success')]
        if successful_senders:
            print(f"\n✅ Successfully processed senders:")
            for sender in successful_senders[:5]:  # Show first 5
                result = sender_results[sender]
                print(f"   📧 {sender}: {result.get('emails_imported', 0)} imported")
        
        # Show failed senders
        failed_senders = [email for email, result in sender_results.items() if not result.get('success')]
        if failed_senders:
            print(f"\n❌ Failed senders:")
            for sender in failed_senders[:5]:  # Show first 5
                result = sender_results[sender]
                print(f"   ❌ {sender}: {result.get('reason', 'unknown')}")
        
        # Show Phase 3 Analytics Summary
        if analytics_report:
            print(f"\n📊 PHASE 3 ANALYTICS SUMMARY")
            print("-" * 30)
            insights = analytics_report.summary_insights
            
            # Import performance
            perf = insights.get('import_performance', {})
            print(f"⚡ Processing Speed: {perf.get('processing_speed', 'N/A')}")
            print(f"📧 Success Rate: {perf.get('success_rate', 0):.1%}")
            print(f"🔍 Duplicates Found: {perf.get('duplicates_found', 0):,}")
            
            # Timeline insights
            timeline = insights.get('timeline_insights', {})
            print(f"📈 Timeline Completeness: {timeline.get('overall_completeness', 'N/A')}")
            print(f"⚠️  Critical Gaps: {timeline.get('critical_gaps', 0)}")
            
            # Sender insights  
            sender = insights.get('sender_insights', {})
            print(f"👥 Total Senders: {sender.get('total_senders', 0):,}")
            print(f"⭐ High-Value Contacts: {sender.get('high_value_contacts', 0)}")
            
            # Action items
            if analytics_report.action_items:
                print(f"\n💡 Key Action Items:")
                for i, action in enumerate(analytics_report.action_items[:3], 1):
                    print(f"   {i}. {action}")
            
            print(f"\n📋 Full analytics report: {analytics_report.report_id}")
    
    def quick_test_import(self, sender_email: str = "service@ringcentral.com") -> bool:
        """
        Performs a quick test import for a specific sender.
        
        Args:
            sender_email: Email address to test with
            
        Returns:
            True if test successful, False otherwise
        """
        print(f"🧪 Quick Test Import for: {sender_email}")
        print("-" * 40)
        
        try:
            result = self.import_all_emails(
                test_mode=True,
                specific_sender=sender_email
            )
            
            if result['success']:
                stats = result['stats']
                if stats['emails_imported'] > 0:
                    print(f"✅ Test successful! Imported {stats['emails_imported']} emails")
                    return True
                else:
                    print("⚠️  Test completed but no emails imported")
                    return False
            else:
                print(f"❌ Test failed: {result.get('reason', 'unknown')}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False


def quick_test() -> bool:
    """Performs a quick test of the import system."""
    importer = EmailImporter()
    return importer.quick_test_import()

def import_emails(pst_path: str = None, test_mode: bool = True, sender: str = None) -> Dict:
    """
    Main function to import emails.
    
    Args:
        pst_path: PST file path
        test_mode: Whether to run in test mode
        sender: Specific sender to import
        
    Returns:
        Import results
    """
    importer = EmailImporter()
    return importer.import_all_emails(pst_path, test_mode, sender) 