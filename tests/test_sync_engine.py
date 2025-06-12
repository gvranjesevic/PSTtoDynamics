import unittest
from sync.sync_engine import SyncEngine, ChangeTracker, ConflictDetector, DataValidator, ConflictResolver, SyncMonitor, SyncDashboard

class TestSyncEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SyncEngine()
        self.tracker = ChangeTracker()
        self.detector = ConflictDetector()
        self.validator = DataValidator()
        self.resolver = ConflictResolver()
        self.monitor = SyncMonitor()

    def test_change_tracking(self):
        src = {'id': '1', 'name': 'Alice', 'email': 'alice@a.com'}
        tgt = {'id': '1', 'name': 'Alice', 'email': 'alice@b.com'}
        changes = self.tracker.track_changes(src, tgt)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['field'], 'email')

    def test_conflict_detection(self):
        changes = [
            {'field': 'email', 'source_value': 'a', 'target_value': 'b', 'timestamp': None}
        ]
        conflicts = self.detector.detect_conflicts(changes)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]['change']['field'], 'email')

    def test_validation(self):
        valid = {'id': '1', 'name': 'Test', 'email': 'test@example.com'}
        invalid = {'id': '1', 'name': 'Test', 'email': 'bad-email'}
        self.assertTrue(self.validator.validate_data(valid))
        self.assertFalse(self.validator.validate_data(invalid))

    def test_sync_logic(self):
        src = {'id': '1', 'name': 'Alice', 'email': 'alice@a.com'}
        tgt = {'id': '1', 'name': 'Alice', 'email': 'alice@b.com'}
        new_src, new_tgt, conflicts = self.engine.sync_data(src, tgt)
        self.assertEqual(new_tgt['email'], 'alice@a.com')
        self.assertEqual(len(conflicts), 1)

    def test_conflict_resolver_last_write_wins(self):
        conflict = {'change': {'field': 'email', 'source_value': 'a', 'target_value': 'b'}}
        result = self.resolver.resolve(conflict, strategy='last_write_wins')
        self.assertEqual(result, 'a')

    def test_conflict_resolver_manual(self):
        conflict = {'change': {'field': 'email', 'source_value': 'a', 'target_value': 'b'}}
        result = self.resolver.resolve(conflict, strategy='manual', user_choice='b')
        self.assertEqual(result, 'b')

    def test_conflict_resolver_merge(self):
        conflict = {'change': {'field': 'email', 'source_value': 'a', 'target_value': 'b'}}
        result = self.resolver.resolve(conflict, strategy='merge')
        self.assertEqual(result, 'a / b')

    def test_conflict_history(self):
        conflict = {'change': {'field': 'email', 'source_value': 'a', 'target_value': 'b'}}
        self.resolver.resolve(conflict, strategy='last_write_wins')
        self.resolver.resolve(conflict, strategy='manual', user_choice='b')
        self.resolver.resolve(conflict, strategy='merge')
        history = self.resolver.get_conflict_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['strategy'], 'last_write_wins')
        self.assertEqual(history[1]['strategy'], 'manual')
        self.assertEqual(history[2]['strategy'], 'merge')

    def test_checksum_generation_and_verification(self):
        data = {'id': '1', 'name': 'Alice', 'email': 'alice@a.com'}
        checksum = self.validator.generate_checksum(data)
        self.assertTrue(self.validator.verify_checksum(data, checksum))
        # Tamper data
        data2 = {'id': '1', 'name': 'Alice', 'email': 'alice@b.com'}
        self.assertFalse(self.validator.verify_checksum(data2, checksum))

    def test_consistency_check(self):
        d1 = {'id': '1', 'name': 'A', 'email': 'a@a.com'}
        d2 = {'id': '1', 'name': 'A', 'email': 'a@a.com'}
        d3 = {'id': '1', 'name': 'B', 'email': 'b@b.com'}
        self.assertTrue(self.validator.check_consistency(d1, d2))
        self.assertFalse(self.validator.check_consistency(d1, d3))

    def test_recovery_mechanism(self):
        src = {'id': '1', 'name': 'Alice', 'email': 'alice@a.com'}
        tgt = {'id': '1', 'name': 'Alice', 'email': 'alice@b.com'}
        self.engine.sync_data(src, tgt)
        # Should be able to recover
        self.assertTrue(self.engine.recover_sync('1'))
        # Non-existent
        self.assertFalse(self.engine.recover_sync('notfound'))

    def test_sync_monitor_and_dashboard(self):
        self.monitor.track_sync('sync', {'source': '1', 'target': '2'})
        self.monitor.track_conflict({'field': 'email'})
        self.monitor.track_error('Test error')
        metrics = self.monitor.get_metrics()
        self.assertEqual(metrics['sync_count'], 1)
        self.assertEqual(metrics['conflict_count'], 1)
        self.assertEqual(metrics['error_count'], 1)
        dashboard = SyncDashboard(self.monitor)
        # Just ensure display methods run without error
        dashboard.display_metrics()
        dashboard.display_logs()

if __name__ == '__main__':
    unittest.main() 