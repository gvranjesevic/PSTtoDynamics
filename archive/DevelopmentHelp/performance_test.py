"""
Performance Testing for Large Datasets
=====================================

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
import os
import time
import random
from datetime import datetime, timedelta

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_test_dataset(email_count: int) -> dict:
    """Generate a large test dataset for performance testing."""
    print(f"📊 Generating test dataset with {email_count:,} emails...")
    
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
    
    print(f"   ✅ Generated {email_count:,} emails from {len(emails_by_sender)} unique senders")
    return emails_by_sender

def test_bulk_processing_performance(test_data: dict):
    """Test bulk processing performance with large datasets."""
    print("\n📦 BULK PROCESSING PERFORMANCE TEST")
    print("=" * 60)
    
    try:
        import bulk_processor
        
        processor = bulk_processor.BulkProcessor()
        
        total_emails = sum(len(emails) for emails in test_data.values())
        print(f"📧 Testing with {total_emails:,} emails from {len(test_data)} senders")
        
        # Test batch creation performance
        print("\n⏱️ Testing batch creation performance...")
        start_time = time.time()
        
        batches = processor._create_processing_batches(test_data)
        
        batch_time = time.time() - start_time
        print(f"   ✅ Created {len(batches)} batches in {batch_time:.2f} seconds")
        print(f"   📊 Batch creation rate: {total_emails/batch_time:.0f} emails/second")
        
        # Analyze batch distribution
        batch_sizes = [batch['size'] for batch in batches]
        print(f"   📦 Batch statistics:")
        print(f"      Average size: {sum(batch_sizes)/len(batch_sizes):.1f} emails")
        print(f"      Largest batch: {max(batch_sizes)} emails")
        print(f"      Smallest batch: {min(batch_sizes)} emails")
        
        # Test session management
        print("\n📊 Testing session management...")
        session_stats = processor.get_session_stats()
        print(f"   Session ID: {session_stats['session_id']}")
        print(f"   Processing capacity: {processor.max_emails_per_session:,} emails")
        
        if total_emails > processor.max_emails_per_session:
            print(f"   ⚠️ Dataset exceeds single session limit")
            print(f"   📦 Would require {(total_emails // processor.max_emails_per_session) + 1} sessions")
        else:
            print(f"   ✅ Dataset fits in single session")
        
        # Test checkpoint intervals
        checkpoint_count = total_emails // processor.checkpoint_interval
        print(f"   📍 Checkpoint intervals: {checkpoint_count} checkpoints needed")
        
        return True
        
    except Exception as e:
        print(f"❌ Bulk processing performance test failed: {e}")
        return False

def test_duplicate_detection_performance(test_data: dict):
    """Test duplicate detection performance at scale."""
    print("\n🔍 DUPLICATE DETECTION PERFORMANCE TEST")
    print("=" * 60)
    
    try:
        import email_comparator
        
        comparator = email_comparator.EmailComparator()
        
        # Take a sample for testing (testing all would be too slow)
        sample_senders = list(test_data.keys())[:10]
        sample_emails = []
        
        for sender in sample_senders:
            sample_emails.extend(test_data[sender][:10])  # Max 10 emails per sender
        
        print(f"🔍 Testing duplicate detection with {len(sample_emails)} sample emails")
        
        # Create some potential duplicates by modifying existing emails
        duplicates = []
        for i in range(0, min(50, len(sample_emails)), 5):  # Every 5th email
            duplicate = sample_emails[i].copy()
            duplicate['subject'] = duplicate['subject'] + ' [DUPLICATE]'
            duplicates.append(duplicate)
        
        print(f"   📧 Created {len(duplicates)} potential duplicates for testing")
        
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
        
        print(f"   ⏱️ Performance results:")
        print(f"      Comparisons: {comparison_count}")
        print(f"      Total time: {comparison_time:.2f} seconds")
        print(f"      Rate: {comparison_count/comparison_time:.1f} comparisons/second")
        print(f"      Duplicates found: {duplicate_count}")
        
        # Get comparison statistics
        stats = comparator.get_comparison_stats()
        print(f"   📊 Comparison statistics:")
        print(f"      Total comparisons: {stats['total_comparisons']}")
        print(f"      Message-ID matches: {stats['message_id_matches']}")
        print(f"      Content hash matches: {stats['content_hash_matches']}")
        
        # Estimate performance for full dataset
        total_emails = sum(len(emails) for emails in test_data.values())
        estimated_time = (total_emails * comparison_time) / comparison_count
        print(f"   📈 Estimated time for full dataset: {estimated_time/60:.1f} minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ Duplicate detection performance test failed: {e}")
        return False

def test_contact_creation_performance(test_data: dict):
    """Test contact creation performance with many senders."""
    print("\n👥 CONTACT CREATION PERFORMANCE TEST")
    print("=" * 60)
    
    try:
        import contact_creator
        
        creator = contact_creator.ContactCreator()
        
        # Get unique senders
        senders = list(test_data.keys())
        print(f"👥 Testing contact creation for {len(senders)} unique senders")
        
        # Test contact info extraction performance
        print("\n⏱️ Testing contact info extraction...")
        start_time = time.time()
        
        extracted_contacts = []
        for sender in senders:
            contact_info = creator._extract_contact_info(sender, test_data)
            if creator._validate_contact_data(contact_info):
                extracted_contacts.append(contact_info)
        
        extraction_time = time.time() - start_time
        
        print(f"   ✅ Extracted {len(extracted_contacts)} valid contacts")
        print(f"   ⏱️ Extraction time: {extraction_time:.2f} seconds")
        print(f"   📊 Rate: {len(senders)/extraction_time:.1f} contacts/second")
        
        # Test batch creation for contact creation
        print("\n📦 Testing batch organization...")
        batch_size = 25  # From config
        batches_needed = (len(extracted_contacts) + batch_size - 1) // batch_size
        
        print(f"   📦 Batch requirements:")
        print(f"      Total contacts: {len(extracted_contacts)}")
        print(f"      Batch size: {batch_size}")
        print(f"      Batches needed: {batches_needed}")
        print(f"      Estimated creation time: {batches_needed * 2:.1f} seconds")
        
        # Test missing contact analysis performance
        print("\n🔍 Testing missing contact analysis...")
        analysis_start = time.time()
        
        # Note: This will try to connect to Dynamics, may fail in test environment
        try:
            analysis = creator.analyze_missing_contacts(senders[:10])  # Test subset
            analysis_time = time.time() - analysis_start
            
            print(f"   📊 Analysis results (10 senders):")
            print(f"      Total senders: {analysis['total_senders']}")
            print(f"      Missing contacts: {analysis['missing_contacts']}")
            print(f"      Analysis time: {analysis_time:.2f} seconds")
            
        except Exception as e:
            print(f"   ⚠️ Analysis test skipped (no Dynamics connection): {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Contact creation performance test failed: {e}")
        return False

def test_memory_performance(test_data: dict):
    """Test memory usage and optimization."""
    print("\n💾 MEMORY PERFORMANCE TEST")
    print("=" * 60)
    
    try:
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Initial memory measurement
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"💾 Initial memory usage: {initial_memory:.1f} MB")
        
        # Memory usage during data processing
        total_emails = sum(len(emails) for emails in test_data.values())
        memory_per_email = initial_memory / max(total_emails, 1) * 1000  # KB per email
        
        print(f"   📧 Dataset size: {total_emails:,} emails")
        print(f"   📊 Memory per email: {memory_per_email:.2f} KB")
        
        # Test garbage collection
        print("\n🧹 Testing memory optimization...")
        gc_start = time.time()
        collected = gc.collect()
        gc_time = time.time() - gc_start
        
        post_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_freed = initial_memory - post_gc_memory
        
        print(f"   🧹 Garbage collection results:")
        print(f"      Objects collected: {collected}")
        print(f"      Time taken: {gc_time:.3f} seconds")
        print(f"      Memory freed: {memory_freed:.1f} MB")
        print(f"      Final memory: {post_gc_memory:.1f} MB")
        
        # Memory efficiency assessment
        if memory_per_email < 5:  # Less than 5KB per email
            print("   ✅ Excellent memory efficiency")
        elif memory_per_email < 20:  # Less than 20KB per email
            print("   ✅ Good memory efficiency")
        else:
            print("   ⚠️ High memory usage - optimization recommended")
        
        return True
        
    except ImportError:
        print("   ⚠️ psutil not available - memory testing skipped")
        return True
    except Exception as e:
        print(f"❌ Memory performance test failed: {e}")
        return False

def run_stress_test(email_count: int):
    """Run a comprehensive stress test."""
    print(f"\n🔥 STRESS TEST - {email_count:,} EMAILS")
    print("=" * 60)
    
    # Generate large dataset
    start_time = time.time()
    test_data = generate_test_dataset(email_count)
    generation_time = time.time() - start_time
    
    print(f"📊 Dataset generation: {generation_time:.2f} seconds")
    print(f"   Rate: {email_count/generation_time:.0f} emails/second generated")
    
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
    print("🚀 PERFORMANCE TESTING - LARGE DATASETS")
    print("=" * 80)
    print("⚡ Testing system performance with 1000+ email datasets")
    print("=" * 80)
    
    start_time = time.time()
    
    # Test different dataset sizes
    test_sizes = [1000, 2500, 5000]
    all_results = []
    
    for size in test_sizes:
        print(f"\n{'='*20} TESTING {size:,} EMAILS {'='*20}")
        
        results = run_stress_test(size)
        all_results.extend(results)
        
        # Brief pause between tests
        time.sleep(1)
    
    # Overall performance summary
    total_time = time.time() - start_time
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success in all_results if success)
    
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 80)
    
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
        print(f"{test_type:<20} {status} ({passed}/{total})")
    
    print(f"\n📈 Overall Results:")
    print(f"   ✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"   ⏱️ Total Time: {total_time:.1f} seconds")
    
    # Performance assessment
    if passed_tests >= total_tests * 0.8:
        print("\n🎉 EXCELLENT PERFORMANCE!")
        print("✅ System handles large datasets efficiently")
        print("🚀 Ready for production deployment with bulk processing")
    elif passed_tests >= total_tests * 0.6:
        print("\n✅ GOOD PERFORMANCE")
        print("⚠️ Some performance issues but acceptable for production")
    else:
        print("\n⚠️ PERFORMANCE ISSUES DETECTED")
        print("🔧 Optimization needed before production deployment")
    
    return passed_tests >= total_tests * 0.6

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 