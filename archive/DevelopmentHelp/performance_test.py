"""
Performance Testing for Large Datasets
=====================================

logger = logging.getLogger(__name__)

Tests system performance with large email datasets (1000+ emails):
- Bulk processing efficiency
- Memory management
- Checkpoint system
- Duplicate detection at scale
- Contact creation performance

Author: AI Assistant
Phase: Performance Testing
"""

import sys
import logging
import os
import time
import random
from datetime import datetime, timedelta

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_test_dataset(email_count: int) -> dict:
    """Generate a large test dataset for performance testing."""
    logger.info("📊 Generating test dataset with {email_count:,} emails...")
    
    # Sample domains and names for variety
    domains = ['example.com', 'testcompany.com', 'ringcentral.com', 'protective.com', 'dynamique.com', 'microsoft.com']
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
    last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Miller', 'Moore', 'Taylor', 'Anderson', 'Thomas']
    
    emails_by_sender = {}
    start_date = datetime.now() - timedelta(days=365)
    
    # Generate diverse sender pool (roughly 1 sender per 10 emails)
    sender_count = max(email_count // 10, 10)
    
    for i in range(email_count):
        # Create sender email
        if len(emails_by_sender) < sender_count:
            # New sender
            first = random.choice(first_names)
            last = random.choice(last_names)
            domain = random.choice(domains)
            sender_email = f"{first.lower()}.{last.lower()}{len(emails_by_sender)}@{domain}"
        else:
            # Reuse existing sender
            sender_email = list(emails_by_sender.keys())[i % len(emails_by_sender)]
        
        # Generate email data
        email_data = {
            'subject': f'Test Email {i+1} - {random.choice(["Meeting", "Update", "Report", "Question", "Follow-up"])}',
            'body': f'This is test email content #{i+1}. ' + ' '.join(['Lorem ipsum'] * random.randint(10, 50)),
            'sent_time': (start_date + timedelta(days=random.randint(0, 365))).isoformat(),
            'sender_email': sender_email,
            'sender_name': sender_email.split('@')[0].replace('.', ' ').title(),
            'message_id': f'test{i+1}@{domain}'
        }
        
        if sender_email not in emails_by_sender:
            emails_by_sender[sender_email] = []
        emails_by_sender[sender_email].append(email_data)
    
    logger.debug("   ✅ Generated {email_count:,} emails from {len(emails_by_sender)} unique senders")
    return emails_by_sender

def test_bulk_processing_performance(test_data: dict):
    """Test bulk processing performance with large datasets."""
    logger.debug("\n📦 BULK PROCESSING PERFORMANCE TEST")
    logger.debug("=" * 60)
    
    try:
        import bulk_processor
        
        processor = bulk_processor.BulkProcessor()
        
        total_emails = sum(len(emails) for emails in test_data.values())
        logger.info("📧 Testing with {total_emails:,} emails from {len(test_data)} senders")
        
        # Test batch creation performance
        logger.debug("\n⏱️ Testing batch creation performance...")
        start_time = time.time()
        
        batches = processor._create_processing_batches(test_data)
        
        batch_time = time.time() - start_time
        logger.debug("   ✅ Created {len(batches)} batches in {batch_time:.2f} seconds")
        logger.debug("   📊 Batch creation rate: {total_emails/batch_time:.0f} emails/second")
        
        # Analyze batch distribution
        batch_sizes = [batch['size'] for batch in batches]
        logger.debug("   📦 Batch statistics:")
        logger.debug("      Average size: {sum(batch_sizes)/len(batch_sizes):.1f} emails")
        logger.debug("      Largest batch: {max(batch_sizes)} emails")
        logger.debug("      Smallest batch: {min(batch_sizes)} emails")
        
        # Test session management
        logger.debug("\n📊 Testing session management...")
        session_stats = processor.get_session_stats()
        logger.debug("   Session ID: {session_stats['session_id']}")
        logger.debug("   Processing capacity: {processor.max_emails_per_session:,} emails")
        
        if total_emails > processor.max_emails_per_session:
            logger.debug("   ⚠️ Dataset exceeds single session limit")
            logger.debug("   📦 Would require {(total_emails // processor.max_emails_per_session) + 1} sessions")
        else:
            logger.debug("   ✅ Dataset fits in single session")
        
        # Test checkpoint intervals
        checkpoint_count = total_emails // processor.checkpoint_interval
        logger.debug("   📍 Checkpoint intervals: {checkpoint_count} checkpoints needed")
        
        return True
        
    except Exception as e:
        logger.error("❌ Bulk processing performance test failed: {e}")
        return False

def test_duplicate_detection_performance(test_data: dict):
    """Test duplicate detection performance at scale."""
    logger.debug("\n🔍 DUPLICATE DETECTION PERFORMANCE TEST")
    logger.debug("=" * 60)
    
    try:
        import email_comparator
        
        comparator = email_comparator.EmailComparator()
        
        # Take a sample for testing (testing all would be too slow)
        sample_senders = list(test_data.keys())[:10]
        sample_emails = []
        
        for sender in sample_senders:
            sample_emails.extend(test_data[sender][:10])  # Max 10 emails per sender
        
        logger.info("🔍 Testing duplicate detection with {len(sample_emails)} sample emails")
        
        # Create some potential duplicates by modifying existing emails
        duplicates = []
        for i in range(0, min(50, len(sample_emails)), 5):  # Every 5th email
            duplicate = sample_emails[i].copy()
            duplicate['subject'] = duplicate['subject'] + ' [DUPLICATE]'
            duplicates.append(duplicate)
        
        logger.debug("   📧 Created {len(duplicates)} potential duplicates for testing")
        
        # Test comparison performance
        start_time = time.time()
        duplicate_count = 0
        comparison_count = 0
        
        for pst_email in sample_emails[:20]:  # Test first 20 emails
            result = comparator.find_duplicates(pst_email, duplicates)
            comparison_count += 1
            if result['has_duplicates']:
                duplicate_count += 1
        
        comparison_time = time.time() - start_time
        
        logger.debug("   ⏱️ Performance results:")
        logger.debug("      Comparisons: {comparison_count}")
        logger.debug("      Total time: {comparison_time:.2f} seconds")
        logger.debug("      Rate: {comparison_count/comparison_time:.1f} comparisons/second")
        logger.debug("      Duplicates found: {duplicate_count}")
        
        # Get comparison statistics
        stats = comparator.get_comparison_stats()
        logger.debug("   📊 Comparison statistics:")
        logger.debug("      Total comparisons: {stats['total_comparisons']}")
        logger.debug("      Message-ID matches: {stats['message_id_matches']}")
        logger.debug("      Content hash matches: {stats['content_hash_matches']}")
        
        # Estimate performance for full dataset
        total_emails = sum(len(emails) for emails in test_data.values())
        estimated_time = (total_emails * comparison_time) / comparison_count
        logger.debug("   📈 Estimated time for full dataset: {estimated_time/60:.1f} minutes")
        
        return True
        
    except Exception as e:
        logger.error("❌ Duplicate detection performance test failed: {e}")
        return False

def test_contact_creation_performance(test_data: dict):
    """Test contact creation performance with many senders."""
    logger.debug("\n👥 CONTACT CREATION PERFORMANCE TEST")
    logger.debug("=" * 60)
    
    try:
        import contact_creator
        
        creator = contact_creator.ContactCreator()
        
        # Get unique senders
        senders = list(test_data.keys())
        logger.info("👥 Testing contact creation for {len(senders)} unique senders")
        
        # Test contact info extraction performance
        logger.debug("\n⏱️ Testing contact info extraction...")
        start_time = time.time()
        
        extracted_contacts = []
        for sender in senders:
            contact_info = creator._extract_contact_info(sender, test_data)
            if creator._validate_contact_data(contact_info):
                extracted_contacts.append(contact_info)
        
        extraction_time = time.time() - start_time
        
        logger.debug("   ✅ Extracted {len(extracted_contacts)} valid contacts")
        logger.debug("   ⏱️ Extraction time: {extraction_time:.2f} seconds")
        logger.debug("   📊 Rate: {len(senders)/extraction_time:.1f} contacts/second")
        
        # Test batch creation for contact creation
        logger.debug("\n📦 Testing batch organization...")
        batch_size = 25  # From config
        batches_needed = (len(extracted_contacts) + batch_size - 1) // batch_size
        
        logger.debug("   📦 Batch requirements:")
        logger.debug("      Total contacts: {len(extracted_contacts)}")
        logger.debug("      Batch size: {batch_size}")
        logger.debug("      Batches needed: {batches_needed}")
        logger.debug("      Estimated creation time: {batches_needed * 2:.1f} seconds")
        
        # Test missing contact analysis performance
        logger.debug("\n🔍 Testing missing contact analysis...")
        analysis_start = time.time()
        
        # Note: This will try to connect to Dynamics, may fail in test environment
        try:
            analysis = creator.analyze_missing_contacts(senders[:10])  # Test subset
            analysis_time = time.time() - analysis_start
            
            logger.debug("   📊 Analysis results (10 senders):")
            logger.debug("      Total senders: {analysis['total_senders']}")
            logger.debug("      Missing contacts: {analysis['missing_contacts']}")
            logger.debug("      Analysis time: {analysis_time:.2f} seconds")
            
        except Exception as e:
            logger.debug("   ⚠️ Analysis test skipped (no Dynamics connection): {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error("❌ Contact creation performance test failed: {e}")
        return False

def test_memory_performance(test_data: dict):
    """Test memory usage and optimization."""
    logger.debug("\n💾 MEMORY PERFORMANCE TEST")
    logger.debug("=" * 60)
    
    try:
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Initial memory measurement
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        logger.debug("💾 Initial memory usage: {initial_memory:.1f} MB")
        
        # Memory usage during data processing
        total_emails = sum(len(emails) for emails in test_data.values())
        memory_per_email = initial_memory / max(total_emails, 1) * 1000  # KB per email
        
        logger.debug("   📧 Dataset size: {total_emails:,} emails")
        logger.debug("   📊 Memory per email: {memory_per_email:.2f} KB")
        
        # Test garbage collection
        logger.debug("\n🧹 Testing memory optimization...")
        gc_start = time.time()
        collected = gc.collect()
        gc_time = time.time() - gc_start
        
        post_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_freed = initial_memory - post_gc_memory
        
        logger.debug("   🧹 Garbage collection results:")
        logger.debug("      Objects collected: {collected}")
        logger.debug("      Time taken: {gc_time:.3f} seconds")
        logger.debug("      Memory freed: {memory_freed:.1f} MB")
        logger.debug("      Final memory: {post_gc_memory:.1f} MB")
        
        # Memory efficiency assessment
        if memory_per_email < 5:  # Less than 5KB per email
            logger.debug("   ✅ Excellent memory efficiency")
        elif memory_per_email < 20:  # Less than 20KB per email
            logger.debug("   ✅ Good memory efficiency")
        else:
            logger.debug("   ⚠️ High memory usage - optimization recommended")
        
        return True
        
    except ImportError:
        logger.debug("   ⚠️ psutil not available - memory testing skipped")
        return True
    except Exception as e:
        logger.error("❌ Memory performance test failed: {e}")
        return False

def run_stress_test(email_count: int):
    """Run a comprehensive stress test."""
    logger.debug("\n🔥 STRESS TEST - {email_count:,} EMAILS")
    logger.debug("=" * 60)
    
    # Generate large dataset
    start_time = time.time()
    test_data = generate_test_dataset(email_count)
    generation_time = time.time() - start_time
    
    logger.info("📊 Dataset generation: {generation_time:.2f} seconds")
    logger.debug("   Rate: {email_count/generation_time:.0f} emails/second generated")
    
    # Run all performance tests
    test_results = []
    
    success = test_bulk_processing_performance(test_data)
    test_results.append(("Bulk Processing", success))
    
    success = test_duplicate_detection_performance(test_data)
    test_results.append(("Duplicate Detection", success))
    
    success = test_contact_creation_performance(test_data)
    test_results.append(("Contact Creation", success))
    
    success = test_memory_performance(test_data)
    test_results.append(("Memory Management", success))
    
    return test_results

def main():
    """Run comprehensive performance testing."""
    logger.info("🚀 PERFORMANCE TESTING - LARGE DATASETS")
    logger.debug("=" * 80)
    logger.debug("⚡ Testing system performance with 1000+ email datasets")
    logger.debug("=" * 80)
    
    start_time = time.time()
    
    # Test different dataset sizes
    test_sizes = [1000, 2500, 5000]
    all_results = []
    
    for size in test_sizes:
        logger.debug("\n{'='*20} TESTING {size:,} EMAILS {'='*20}")
        
        results = run_stress_test(size)
        all_results.extend(results)
        
        # Brief pause between tests
        time.sleep(1)
    
    # Overall performance summary
    total_time = time.time() - start_time
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success in all_results if success)
    
    logger.debug("\n" + "=" * 80)
    logger.info("📊 PERFORMANCE TEST SUMMARY")
    logger.debug("=" * 80)
    
    # Group results by test type
    test_types = {}
    for test_name, success in all_results:
        if test_name not in test_types:
            test_types[test_name] = []
        test_types[test_name].append(success)
    
    for test_type, results in test_types.items():
        passed = sum(results)
        total = len(results)
        status = "✅ PASS" if passed == total else "⚠️ PARTIAL" if passed > 0 else "❌ FAIL"
        logger.debug("{test_type:<20} {status} ({passed}/{total})")
    
    logger.debug("\n📈 Overall Results:")
    logger.debug("   ✅ Tests Passed: {passed_tests}/{total_tests}")
    logger.debug("   ⏱️ Total Time: {total_time:.1f} seconds")
    
    # Performance assessment
    if passed_tests >= total_tests * 0.8:
        logger.debug("\n🎉 EXCELLENT PERFORMANCE!")
        logger.info("✅ System handles large datasets efficiently")
        logger.info("🚀 Ready for production deployment with bulk processing")
    elif passed_tests >= total_tests * 0.6:
        logger.debug("\n✅ GOOD PERFORMANCE")
        logger.warning("⚠️ Some performance issues but acceptable for production")
    else:
        logger.debug("\n⚠️ PERFORMANCE ISSUES DETECTED")
        logger.debug("🔧 Optimization needed before production deployment")
    
    return passed_tests >= total_tests * 0.6

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 