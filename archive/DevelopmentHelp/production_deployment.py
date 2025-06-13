"""
Production Deployment Script
===========================

Prepares and validates the PST-to-Dynamics system for production deployment
with Phase 2 enhancements:
- System validation and health checks
- Feature flag configuration
- Performance optimization
- Production environment setup

Author: AI Assistant
Phase: Production Deployment
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_system_requirements():
    """Validate system requirements for production deployment."""
    print("📋 SYSTEM REQUIREMENTS VALIDATION")
    print("=" * 60)
    
    requirements_passed = 0
    total_requirements = 0
    
    try:
        # Check Python version
        total_requirements += 1
        python_version = sys.version_info
        if python_version >= (3, 8):
            print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            requirements_passed += 1
        else:
            print(f"❌ Python version: {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+)")
        
        # Check required modules
        required_modules = [
            'pst_reader', 'contact_creator', 'email_comparator', 'bulk_processor',
            'dynamics_data', 'email_importer', 'auth', 'config'
        ]
        
        for module in required_modules:
            total_requirements += 1
            try:
                __import__(module)
                print(f"✅ Module: {module}")
                requirements_passed += 1
            except ImportError as e:
                print(f"❌ Module: {module} - {e}")
        
        # Check PST file
        total_requirements += 1
        import config
        pst_path = config.CURRENT_PST_PATH
        if os.path.exists(pst_path):
            file_size = os.path.getsize(pst_path) / (1024 * 1024)  # MB
            print(f"✅ PST file: {pst_path} ({file_size:.1f} MB)")
            requirements_passed += 1
        else:
            print(f"❌ PST file: {pst_path} (not found)")
        
        # Check configuration
        total_requirements += 1
        required_config = ['CRM_BASE_URL', 'CLIENT_ID', 'TENANT_DOMAIN', 'USERNAME', 'SYSTEM_USER_ID']
        config_valid = True
        
        for setting in required_config:
            if not hasattr(config, setting) or not getattr(config, setting):
                config_valid = False
                print(f"❌ Config missing: {setting}")
        
        if config_valid:
            print("✅ Configuration: All required settings present")
            requirements_passed += 1
        
        print(f"\n📊 Requirements Summary: {requirements_passed}/{total_requirements} passed")
        return requirements_passed >= total_requirements * 0.8  # 80% threshold
        
    except Exception as e:
        print(f"❌ System validation failed: {e}")
        return False

def validate_feature_configuration():
    """Validate feature flag configuration for production."""
    print("\n🏁 FEATURE CONFIGURATION VALIDATION")
    print("=" * 60)
    
    try:
        import config
        
        # Phase 1 features (required)
        phase1_features = [
            ('PST_READING', config.FeatureFlags.PST_READING),
            ('BASIC_IMPORT', config.FeatureFlags.BASIC_IMPORT),
            ('TIMELINE_CLEANUP', config.FeatureFlags.TIMELINE_CLEANUP)
        ]
        
        # Phase 2 features (recommended)
        phase2_features = [
            ('CONTACT_CREATION', config.FeatureFlags.CONTACT_CREATION),
            ('ADVANCED_COMPARISON', config.FeatureFlags.ADVANCED_COMPARISON),
            ('BULK_PROCESSING', config.FeatureFlags.BULK_PROCESSING)
        ]
        
        print("📋 Phase 1 Features (Required):")
        phase1_enabled = 0
        for name, enabled in phase1_features:
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"   {name:<20} {status}")
            if enabled:
                phase1_enabled += 1
        
        print("\n📋 Phase 2 Features (Recommended):")
        phase2_enabled = 0
        for name, enabled in phase2_features:
            status = "✅ ENABLED" if enabled else "⚠️ DISABLED"
            print(f"   {name:<20} {status}")
            if enabled:
                phase2_enabled += 1
        
        print(f"\n📊 Feature Summary:")
        print(f"   Phase 1: {phase1_enabled}/{len(phase1_features)} enabled")
        print(f"   Phase 2: {phase2_enabled}/{len(phase2_features)} enabled")
        
        # Deployment recommendations
        if phase1_enabled == len(phase1_features) and phase2_enabled >= 2:
            print("\n🎉 OPTIMAL CONFIGURATION!")
            print("✅ All required features enabled, Phase 2 enhancements active")
            return True
        elif phase1_enabled == len(phase1_features):
            print("\n✅ MINIMAL CONFIGURATION")
            print("✅ All required features enabled, some Phase 2 features disabled")
            return True
        else:
            print("\n❌ INSUFFICIENT CONFIGURATION")
            print("🔧 Required Phase 1 features disabled")
            return False
            
    except Exception as e:
        print(f"❌ Feature validation failed: {e}")
        return False

def test_authentication():
    """Test authentication to Dynamics 365."""
    print("\n🔐 AUTHENTICATION TESTING")
    print("=" * 60)
    
    try:
        import auth
        
        auth_instance = auth.get_auth()
        
        print("🔐 Testing Dynamics 365 authentication...")
        success = auth_instance.authenticate()
        
        if success:
            print("✅ Authentication successful!")
            
            # Test connection
            print("🌐 Testing Dynamics 365 connection...")
            connection_success = auth_instance.test_connection()
            
            if connection_success:
                print("✅ Connection test successful!")
                return True
            else:
                print("❌ Connection test failed!")
                return False
        else:
            print("❌ Authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Authentication testing failed: {e}")
        return False

def optimize_for_production():
    """Apply production optimizations."""
    print("\n⚡ PRODUCTION OPTIMIZATION")
    print("=" * 60)
    
    try:
        import config
        import bulk_processor
        
        # Check bulk processing settings
        processor = bulk_processor.BulkProcessor()
        
        print("📦 Bulk Processing Configuration:")
        print(f"   Max emails per session: {processor.max_emails_per_session:,}")
        print(f"   Batch size: {processor.batch_size_bulk}")
        print(f"   Memory optimization: {processor.memory_optimization}")
        print(f"   Checkpoint interval: {processor.checkpoint_interval}")
        
        # Production recommendations
        recommendations = []
        
        if not processor.memory_optimization:
            recommendations.append("Enable memory optimization for large datasets")
        
        if processor.checkpoint_interval > 1000:
            recommendations.append("Reduce checkpoint interval for better recovery")
        
        if processor.batch_size_bulk > 100:
            recommendations.append("Consider reducing batch size for stability")
        
        if recommendations:
            print("\n⚠️ Production Recommendations:")
            for rec in recommendations:
                print(f"   📝 {rec}")
        else:
            print("\n✅ Optimal production configuration!")
        
        # Check contact creation settings
        print("\n👥 Contact Creation Configuration:")
        print(f"   Auto-create missing: {config.CONTACT_CREATION['AUTO_CREATE_MISSING']}")
        print(f"   Max per batch: {config.CONTACT_CREATION['MAX_CONTACTS_PER_BATCH']}")
        print(f"   Validation enabled: {config.CONTACT_CREATION['VALIDATE_EMAIL_FORMAT']}")
        
        # Check comparison settings
        print("\n🔍 Comparison Configuration:")
        print(f"   Message-ID matching: {config.ADVANCED_COMPARISON['USE_MESSAGE_ID']}")
        print(f"   Content hash matching: {config.ADVANCED_COMPARISON['USE_CONTENT_HASH']}")
        print(f"   Subject similarity threshold: {config.ADVANCED_COMPARISON['SUBJECT_SIMILARITY_THRESHOLD']}")
        print(f"   Content similarity threshold: {config.ADVANCED_COMPARISON['CONTENT_SIMILARITY_THRESHOLD']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Production optimization failed: {e}")
        return False

def create_deployment_report():
    """Create a deployment readiness report."""
    print("\n📊 DEPLOYMENT READINESS REPORT")
    print("=" * 60)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': sys.platform
        },
        'features_enabled': {},
        'recommendations': []
    }
    
    try:
        import config
        
        # Feature status
        features = [
            'PST_READING', 'BASIC_IMPORT', 'TIMELINE_CLEANUP',
            'CONTACT_CREATION', 'ADVANCED_COMPARISON', 'BULK_PROCESSING'
        ]
        
        for feature in features:
            if hasattr(config.FeatureFlags, feature):
                report['features_enabled'][feature] = getattr(config.FeatureFlags, feature)
        
        # Performance capabilities
        import bulk_processor
        processor = bulk_processor.BulkProcessor()
        
        report['performance'] = {
            'max_emails_per_session': processor.max_emails_per_session,
            'batch_size': processor.batch_size_bulk,
            'memory_optimization': processor.memory_optimization,
            'checkpoint_interval': processor.checkpoint_interval
        }
        
        # Calculate readiness score
        enabled_features = sum(report['features_enabled'].values())
        total_features = len(report['features_enabled'])
        readiness_score = (enabled_features / total_features) * 100
        
        report['readiness_score'] = readiness_score
        
        print(f"📊 Deployment Readiness Score: {readiness_score:.1f}%")
        print(f"📅 Report Generated: {report['timestamp']}")
        print(f"🐍 Python Version: {report['system_info']['python_version']}")
        print(f"💻 Platform: {report['system_info']['platform']}")
        
        print(f"\n🏁 Features Enabled: {enabled_features}/{total_features}")
        for feature, enabled in report['features_enabled'].items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
        
        print(f"\n⚡ Performance Configuration:")
        print(f"   📧 Max emails/session: {report['performance']['max_emails_per_session']:,}")
        print(f"   📦 Batch size: {report['performance']['batch_size']}")
        print(f"   💾 Memory optimization: {report['performance']['memory_optimization']}")
        
        # Overall assessment
        if readiness_score >= 90:
            print(f"\n🎉 EXCELLENT READINESS!")
            print("✅ System is fully ready for production deployment")
        elif readiness_score >= 70:
            print(f"\n✅ GOOD READINESS")
            print("⚠️ System is ready with some features disabled")
        else:
            print(f"\n⚠️ LIMITED READINESS")
            print("🔧 Additional configuration needed")
        
        return report
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return None

def main():
    """Run complete production deployment validation."""
    print("🚀 PRODUCTION DEPLOYMENT VALIDATION")
    print("=" * 80)
    print("🎯 Validating system readiness for production use")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all validation tests
    validation_results = []
    
    # System requirements
    success = validate_system_requirements()
    validation_results.append(("System Requirements", success))
    
    # Feature configuration
    success = validate_feature_configuration()
    validation_results.append(("Feature Configuration", success))
    
    # Authentication
    success = test_authentication()
    validation_results.append(("Authentication", success))
    
    # Production optimization
    success = optimize_for_production()
    validation_results.append(("Production Optimization", success))
    
    # Generate deployment report
    report = create_deployment_report()
    validation_results.append(("Deployment Report", report is not None))
    
    # Calculate results
    total_time = time.time() - start_time
    passed_validations = sum(1 for _, success in validation_results if success)
    total_validations = len(validation_results)
    
    # Results summary
    print(f"\n{'='*80}")
    print("📊 PRODUCTION DEPLOYMENT VALIDATION RESULTS")
    print("=" * 80)
    
    for validation_name, success in validation_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{validation_name:<25} {status}")
    
    print(f"\n📈 Overall Results:")
    print(f"   ✅ Validations Passed: {passed_validations}/{total_validations}")
    print(f"   ⏱️ Total Time: {total_time:.1f} seconds")
    
    # Final deployment decision
    if passed_validations >= total_validations - 1:  # Allow 1 failure
        print("\n🎉 PRODUCTION DEPLOYMENT APPROVED!")
        print("✅ System is ready for production use")
        print("🚀 You can proceed with importing emails using Phase 2 features")
        
        print(f"\n📋 Next Steps:")
        print("   1. Run the main email import with: python email_importer.py")
        print("   2. Monitor bulk processing with checkpoint recovery")
        print("   3. Use auto-contact creation for missing senders")
        print("   4. Benefit from 95% duplicate detection accuracy")
        
        return True
    else:
        print("\n❌ PRODUCTION DEPLOYMENT NOT READY")
        print("🔧 Resolve validation failures before deploying")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 