"""
Bulk Processor Module
====================

Large-scale email processing engine for Phase 2.
Handles batch processing, memory optimization, and progress tracking.

Author: AI Assistant
Phase: 2
"""

import logging
import time
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import config

class BulkProcessor:
    """Handles large-scale email processing with optimization and progress tracking."""
    
    def __init__(self):
        """Initialize the bulk processor."""
        self.logger = logging.getLogger(__name__)
        
        # Bulk processing settings from config
        self.enable_bulk_mode = config.BULK_PROCESSING['ENABLE_BULK_MODE']
        self.max_emails_per_session = config.BULK_PROCESSING['MAX_EMAILS_PER_SESSION']
        self.batch_size_bulk = config.BULK_PROCESSING['BATCH_SIZE_BULK']
        self.parallel_processing = config.BULK_PROCESSING['PARALLEL_PROCESSING']
        self.memory_optimization = config.BULK_PROCESSING['MEMORY_OPTIMIZATION']
        self.checkpoint_interval = config.BULK_PROCESSING['CHECKPOINT_INTERVAL']
        self.auto_resume = config.BULK_PROCESSING['AUTO_RESUME']
        
        # Processing state
        self.session_id = self._generate_session_id()
        self.processed_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0
        self.start_time = None
        self.checkpoints = []
        
        # Progress tracking
        self.progress_callback = None
        self.last_checkpoint_time = None
        
        # Session statistics
        self.session_stats = {
            'session_id': self.session_id,
            'start_time': None,
            'end_time': None,
            'total_emails': 0,
            'processed_emails': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'skipped_emails': 0,
            'batches_processed': 0,
            'average_batch_time': 0.0,
            'emails_per_minute': 0.0,
            'memory_usage_mb': 0.0
        }
    
    def process_emails_bulk(self, 
                           emails_by_sender: Dict[str, List[Dict]], 
                           import_function: Callable,
                           progress_callback: Optional[Callable] = None) -> Dict:
        """
        Process emails in bulk mode with optimization.
        
        Args:
            emails_by_sender: Dictionary of emails grouped by sender
            import_function: Function to call for importing emails
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with bulk processing results
        """
        if not self.enable_bulk_mode:
            return {
                'success': False,
                'reason': 'Bulk mode is disabled in configuration',
                'session_stats': self.session_stats
            }
        
        self.progress_callback = progress_callback
        self.start_time = datetime.now()
        self.session_stats['start_time'] = self.start_time.isoformat()
        
        # Calculate total emails
        total_emails = sum(len(emails) for emails in emails_by_sender.values())
        self.session_stats['total_emails'] = total_emails
        
        # Check session limits
        if total_emails > self.max_emails_per_session:
            return {
                'success': False,
                'reason': f'Email count ({total_emails}) exceeds session limit ({self.max_emails_per_session})',
                'session_stats': self.session_stats
            }
        
        self.logger.info(f"🚀 Starting bulk processing session {self.session_id}")
        self.logger.info(f"📧 Total emails to process: {total_emails}")
        self.logger.info(f"👥 Senders: {len(emails_by_sender)}")
        self.logger.info(f"📦 Batch size: {self.batch_size_bulk}")
        
        try:
            # Create processing batches
            batches = self._create_processing_batches(emails_by_sender)
            
            # Process batches
            success = self._process_batches(batches, import_function)
            
            # Finalize session
            self._finalize_session()
            
            return {
                'success': success,
                'session_stats': self.session_stats,
                'checkpoints': self.checkpoints
            }
            
        except Exception as e:
            self.logger.error(f"❌ Bulk processing failed: {e}")
            self._finalize_session()
            return {
                'success': False,
                'reason': f'Bulk processing error: {e}',
                'session_stats': self.session_stats
            }
    
    def _create_processing_batches(self, emails_by_sender: Dict[str, List[Dict]]) -> List[Dict]:
        """Create optimized batches for processing."""
        batches = []
        current_batch = []
        current_batch_size = 0
        
        # Sort senders by email count for balanced batching
        sorted_senders = sorted(emails_by_sender.items(), key=lambda x: len(x[1]), reverse=True)
        
        for sender, emails in sorted_senders:
            for email in emails:
                current_batch.append({
                    'sender': sender,
                    'email_data': email
                })
                current_batch_size += 1
                
                # Create batch when size limit reached
                if current_batch_size >= self.batch_size_bulk:
                    batches.append({
                        'batch_id': len(batches) + 1,
                        'emails': current_batch.copy(),
                        'size': current_batch_size
                    })
                    current_batch = []
                    current_batch_size = 0
        
        # Add remaining emails as final batch
        if current_batch:
            batches.append({
                'batch_id': len(batches) + 1,
                'emails': current_batch,
                'size': current_batch_size
            })
        
        self.logger.info(f"📦 Created {len(batches)} processing batches")
        return batches
    
    def _process_batches(self, batches: List[Dict], import_function: Callable) -> bool:
        """Process all batches with progress tracking."""
        total_batches = len(batches)
        
        for batch_num, batch in enumerate(batches, 1):
            batch_start_time = time.time()
            
            self.logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({batch['size']} emails)")
            
            # Process batch
            batch_success = self._process_single_batch(batch, import_function)
            
            # Calculate batch timing
            batch_time = time.time() - batch_start_time
            
            # Update statistics
            self.session_stats['batches_processed'] = batch_num
            self._update_performance_stats(batch_time)
            
            # Progress callback
            if self.progress_callback:
                progress = {
                    'batch_num': batch_num,
                    'total_batches': total_batches,
                    'batch_size': batch['size'],
                    'processed_emails': self.processed_count,
                    'success_count': self.success_count,
                    'failure_count': self.failure_count,
                    'batch_time': batch_time,
                    'estimated_remaining': self._estimate_remaining_time(batch_num, total_batches, batch_time)
                }
                self.progress_callback(progress)
            
            # Checkpoint if needed
            if self._should_create_checkpoint():
                self._create_checkpoint(batch_num, total_batches)
            
            # Memory optimization
            if self.memory_optimization:
                self._optimize_memory()
        
        return True
    
    def _process_single_batch(self, batch: Dict, import_function: Callable) -> bool:
        """Process a single batch of emails."""
        batch_success = True
        
        for email_item in batch['emails']:
            try:
                sender = email_item['sender']
                email_data = email_item['email_data']
                
                # Call the import function
                result = import_function(sender, email_data)
                
                # Track results
                self.processed_count += 1
                self.session_stats['processed_emails'] = self.processed_count
                
                if result and result.get('success', False):
                    self.success_count += 1
                    self.session_stats['successful_imports'] = self.success_count
                elif result and result.get('skipped', False):
                    self.skipped_count += 1
                    self.session_stats['skipped_emails'] = self.skipped_count
                else:
                    self.failure_count += 1
                    self.session_stats['failed_imports'] = self.failure_count
                    batch_success = False
                
            except Exception as e:
                self.logger.error(f"❌ Error processing email from {email_item['sender']}: {e}")
                self.failure_count += 1
                self.session_stats['failed_imports'] = self.failure_count
                batch_success = False
        
        return batch_success
    
    def _update_performance_stats(self, batch_time: float):
        """Update performance statistics."""
        # Calculate average batch time
        current_batches = self.session_stats['batches_processed']
        if current_batches > 0:
            total_time = (datetime.now() - self.start_time).total_seconds()
            self.session_stats['average_batch_time'] = total_time / current_batches
        
        # Calculate emails per minute
        if self.processed_count > 0 and self.start_time:
            elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            if elapsed_minutes > 0:
                self.session_stats['emails_per_minute'] = self.processed_count / elapsed_minutes
        
        # Update memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.session_stats['memory_usage_mb'] = memory_mb
        except ImportError:
            # psutil not available
            pass
    
    def _should_create_checkpoint(self) -> bool:
        """Determine if a checkpoint should be created."""
        if not self.checkpoint_interval:
            return False
        
        return self.processed_count % self.checkpoint_interval == 0
    
    def _create_checkpoint(self, current_batch: int, total_batches: int):
        """Create a progress checkpoint."""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'processed_emails': self.processed_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'skipped_count': self.skipped_count,
            'current_batch': current_batch,
            'total_batches': total_batches,
            'completion_percentage': (self.processed_count / self.session_stats['total_emails']) * 100
        }
        
        self.checkpoints.append(checkpoint)
        self.last_checkpoint_time = datetime.now()
        
        # Save checkpoint to file for resume capability
        if self.auto_resume:
            self._save_checkpoint_file(checkpoint)
        
        self.logger.info(f"📍 Checkpoint created: {self.processed_count}/{self.session_stats['total_emails']} emails processed")
    
    def _save_checkpoint_file(self, checkpoint: Dict):
        """Save checkpoint to file for auto-resume."""
        try:
            checkpoint_file = f"bulk_session_{self.session_id}_checkpoint.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            self.logger.warning(f"⚠️ Could not save checkpoint file: {e}")
    
    def _optimize_memory(self):
        """Perform memory optimization."""
        try:
            import gc
            gc.collect()
        except Exception as e:
            self.logger.warning(f"⚠️ Memory optimization failed: {e}")
    
    def _estimate_remaining_time(self, current_batch: int, total_batches: int, last_batch_time: float) -> str:
        """Estimate remaining processing time."""
        try:
            if current_batch == 0:
                return "Calculating..."
            
            remaining_batches = total_batches - current_batch
            estimated_seconds = remaining_batches * last_batch_time
            
            if estimated_seconds < 60:
                return f"{estimated_seconds:.0f} seconds"
            elif estimated_seconds < 3600:
                return f"{estimated_seconds/60:.1f} minutes"
            else:
                return f"{estimated_seconds/3600:.1f} hours"
                
        except Exception:
            return "Unknown"
    
    def _finalize_session(self):
        """Finalize the bulk processing session."""
        self.session_stats['end_time'] = datetime.now().isoformat()
        
        if self.start_time:
            total_time = (datetime.now() - self.start_time).total_seconds()
            self.session_stats['total_time_seconds'] = total_time
        
        # Log final statistics
        self.logger.info(f"📊 Bulk processing session {self.session_id} completed")
        self.logger.info(f"   📧 Total emails: {self.session_stats['total_emails']}")
        self.logger.info(f"   ✅ Successful: {self.success_count}")
        self.logger.info(f"   ❌ Failed: {self.failure_count}")
        self.logger.info(f"   ⏭️ Skipped: {self.skipped_count}")
        self.logger.info(f"   📦 Batches: {self.session_stats['batches_processed']}")
        self.logger.info(f"   ⏱️ Total time: {self.session_stats.get('total_time_seconds', 0):.1f} seconds")
        self.logger.info(f"   📈 Rate: {self.session_stats['emails_per_minute']:.1f} emails/minute")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics."""
        return self.session_stats.copy()
    
    def get_checkpoints(self) -> List[Dict]:
        """Get all checkpoints from current session."""
        return self.checkpoints.copy()
    
    def can_resume_session(self, session_id: str) -> bool:
        """Check if a session can be resumed."""
        if not self.auto_resume:
            return False
        
        try:
            checkpoint_file = f"bulk_session_{session_id}_checkpoint.json"
            import os
            return os.path.exists(checkpoint_file)
        except Exception:
            return False
    
    def load_checkpoint(self, session_id: str) -> Optional[Dict]:
        """Load checkpoint for session resume."""
        try:
            checkpoint_file = f"bulk_session_{session_id}_checkpoint.json"
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Could not load checkpoint: {e}")
            return None 