"""
Smart Import Optimization Engine - Phase 4.2 Module

This module provides intelligent optimization capabilities for email import operations,
including dynamic batch sizing, performance prediction, resource optimization, and
automated tuning based on machine learning insights.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
import psutil
import time
import statistics
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading
import pickle
import os
from scipy.optimize import minimize, differential_evolution
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization analysis"""
    timestamp: datetime
    batch_size: int
    processing_time: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    emails_per_second: float
    error_count: int
    throughput: float

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation with confidence scoring"""
    category: str
    recommendation: str
    confidence: float
    expected_improvement: float
    implementation_priority: str  # 'high', 'medium', 'low'
    estimated_impact: str

@dataclass
class ResourcePrediction:
    """Predicted resource requirements for import operations"""
    estimated_duration: float
    predicted_memory: float
    predicted_cpu: float
    recommended_batch_size: int
    confidence: float
    risk_factors: List[str]

class SmartImportOptimizer:
    """
    Advanced optimization engine for email import operations.
    
    Capabilities:
    - Dynamic batch size optimization based on system performance
    - Real-time performance monitoring and tuning
    - Predictive resource usage estimation
    - Intelligent scheduling and prioritization
    - Automated error prevention and recovery
    - Machine learning-based optimization
    """
    
    def __init__(self, analytics_db_path: str = "analytics.db"):
        """Initialize the Smart Import Optimizer"""
        self.analytics_db_path = analytics_db_path
        self.optimization_db_path = "optimization.db"
        
        # Performance tracking
        self.performance_history = deque(maxlen=1000)
        self.current_metrics = None
        self.optimization_models = {}
        
        # Optimization parameters
        self.current_batch_size = 50  # Default batch size
        self.min_batch_size = 5
        self.max_batch_size = 500
        self.optimization_interval = 10  # Optimize every 10 batches
        self.batch_counter = 0
        
        # Performance thresholds
        self.target_success_rate = 0.95
        self.max_memory_usage = 0.8  # 80% of available memory
        self.max_cpu_usage = 0.9     # 90% of CPU
        self.target_throughput = 1000  # emails per minute
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Initialize database
        self.init_optimization_database()
        
        logger.info("Smart Import Optimizer initialized successfully")
    
    def init_optimization_database(self):
        """Initialize optimization tracking database"""
        try:
            conn = sqlite3.connect(self.optimization_db_path)
            cursor = conn.cursor()
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    batch_size INTEGER,
                    processing_time REAL,
                    memory_usage REAL,
                    cpu_usage REAL,
                    success_rate REAL,
                    emails_per_second REAL,
                    error_count INTEGER,
                    throughput REAL
                )
            """)
            
            # Optimization recommendations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    category TEXT,
                    recommendation TEXT,
                    confidence REAL,
                    expected_improvement REAL,
                    implementation_priority TEXT,
                    estimated_impact TEXT,
                    applied BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Resource predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    email_count INTEGER,
                    estimated_duration REAL,
                    predicted_memory REAL,
                    predicted_cpu REAL,
                    recommended_batch_size INTEGER,
                    confidence REAL,
                    actual_duration REAL DEFAULT NULL,
                    actual_memory REAL DEFAULT NULL,
                    actual_cpu REAL DEFAULT NULL,
                    prediction_accuracy REAL DEFAULT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Optimization database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing optimization database: {e}")
    
    def start_performance_monitoring(self):
        """Start real-time performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_performance)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Performance monitoring started")
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    def _monitor_performance(self):
        """Background performance monitoring thread"""
        while self.monitoring_active:
            try:
                # Collect current system metrics
                memory_info = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                current_time = datetime.now()
                
                # Update current metrics if batch is in progress
                if self.current_metrics:
                    self.current_metrics.memory_usage = memory_info.percent / 100
                    self.current_metrics.cpu_usage = cpu_percent / 100
                    self.current_metrics.timestamp = current_time
                
                # Check for optimization triggers
                if len(self.performance_history) > 5:
                    self._check_optimization_triggers()
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(10)  # Wait longer on error
    
    def start_batch_tracking(self, batch_size: int, email_count: int) -> str:
        """Start tracking a new batch operation"""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{batch_size}"
        
        self.current_metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            batch_size=batch_size,
            processing_time=0.0,
            memory_usage=0.0,
            cpu_usage=0.0,
            success_rate=0.0,
            emails_per_second=0.0,
            error_count=0,
            throughput=0.0
        )
        
        logger.info(f"Started tracking batch {batch_id} with {email_count} emails")
        return batch_id
    
    def update_batch_progress(self, processed_emails: int, success_count: int, error_count: int):
        """Update batch processing progress"""
        if not self.current_metrics:
            return
        
        elapsed_time = (datetime.now() - self.current_metrics.timestamp).total_seconds()
        
        if elapsed_time > 0:
            self.current_metrics.processing_time = elapsed_time
            self.current_metrics.emails_per_second = processed_emails / elapsed_time
            self.current_metrics.throughput = (processed_emails / elapsed_time) * 60  # per minute
        
        if processed_emails > 0:
            self.current_metrics.success_rate = success_count / processed_emails
        
        self.current_metrics.error_count = error_count
    
    def complete_batch_tracking(self, total_processed: int, total_success: int, total_errors: int):
        """Complete batch tracking and record metrics"""
        if not self.current_metrics:
            return
        
        # Finalize metrics
        elapsed_time = (datetime.now() - self.current_metrics.timestamp).total_seconds()
        self.current_metrics.processing_time = elapsed_time
        
        if total_processed > 0:
            self.current_metrics.success_rate = total_success / total_processed
            if elapsed_time > 0:
                self.current_metrics.emails_per_second = total_processed / elapsed_time
                self.current_metrics.throughput = (total_processed / elapsed_time) * 60
        
        self.current_metrics.error_count = total_errors
        
        # Store metrics
        self.performance_history.append(self.current_metrics)
        self._store_performance_metrics(self.current_metrics)
        
        # Increment batch counter and check for optimization
        self.batch_counter += 1
        if self.batch_counter % self.optimization_interval == 0:
            self._optimize_batch_size()
        
        logger.info(f"Batch completed: {total_processed} emails, "
                   f"{self.current_metrics.success_rate:.1%} success rate, "
                   f"{self.current_metrics.throughput:.1f} emails/min")
        
        self.current_metrics = None
    
    def predict_batch_performance(self, email_count: int, email_characteristics: Dict[str, Any] = None) -> ResourcePrediction:
        """Predict performance for a batch of emails"""
        try:
            # Use historical data for prediction
            if len(self.performance_history) < 3:
                # Not enough data, use defaults
                return ResourcePrediction(
                    estimated_duration=email_count / 1000.0 * 60,  # Assume 1000 emails/min
                    predicted_memory=min(0.5, email_count / 10000),  # Rough estimate
                    predicted_cpu=0.6,
                    recommended_batch_size=self.current_batch_size,
                    confidence=0.3,
                    risk_factors=["Insufficient historical data"]
                )
            
            # Analyze historical performance
            recent_metrics = list(self.performance_history)[-10:]  # Last 10 batches
            
            # Calculate averages and trends
            avg_throughput = statistics.mean([m.throughput for m in recent_metrics if m.throughput > 0])
            avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
            avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
            avg_success_rate = statistics.mean([m.success_rate for m in recent_metrics])
            
            # Predict duration based on throughput
            if avg_throughput > 0:
                estimated_duration = (email_count / avg_throughput) * 60  # in seconds
            else:
                estimated_duration = email_count / 1000.0 * 60
            
            # Predict resource usage with scaling
            scale_factor = email_count / 100  # Assume 100 emails as base
            predicted_memory = min(0.9, avg_memory * (1 + scale_factor * 0.01))
            predicted_cpu = min(0.95, avg_cpu * (1 + scale_factor * 0.005))
            
            # Recommend optimal batch size
            recommended_batch_size = self._calculate_optimal_batch_size(
                email_count, avg_throughput, avg_memory, avg_cpu
            )
            
            # Calculate confidence based on data consistency
            throughput_variance = statistics.stdev([m.throughput for m in recent_metrics if m.throughput > 0])
            confidence = max(0.1, min(0.95, 1.0 - (throughput_variance / avg_throughput)))
            
            # Identify risk factors
            risk_factors = []
            if predicted_memory > 0.8:
                risk_factors.append("High memory usage predicted")
            if predicted_cpu > 0.9:
                risk_factors.append("High CPU usage predicted")
            if avg_success_rate < 0.9:
                risk_factors.append("Low historical success rate")
            if email_count > 1000:
                risk_factors.append("Large batch size")
            
            prediction = ResourcePrediction(
                estimated_duration=estimated_duration,
                predicted_memory=predicted_memory,
                predicted_cpu=predicted_cpu,
                recommended_batch_size=recommended_batch_size,
                confidence=confidence,
                risk_factors=risk_factors
            )
            
            # Store prediction for validation
            self._store_resource_prediction(email_count, prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting batch performance: {e}")
            return ResourcePrediction(
                estimated_duration=email_count / 500.0 * 60,
                predicted_memory=0.5,
                predicted_cpu=0.7,
                recommended_batch_size=50,
                confidence=0.1,
                risk_factors=["Prediction error occurred"]
            )
    
    def optimize_import_schedule(self, import_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize the order and timing of import requests"""
        try:
            # Sort requests by priority and resource requirements
            prioritized_requests = []
            
            for request in import_requests:
                email_count = request.get('email_count', 0)
                priority = request.get('priority', 'medium')
                
                # Predict resource requirements
                prediction = self.predict_batch_performance(email_count)
                
                # Calculate priority score
                priority_scores = {'high': 3, 'medium': 2, 'low': 1}
                priority_score = priority_scores.get(priority, 2)
                
                # Calculate efficiency score (emails per minute predicted)
                efficiency_score = email_count / max(prediction.estimated_duration / 60, 1)
                
                # Combined score
                combined_score = priority_score * 100 + efficiency_score
                
                optimized_request = request.copy()
                optimized_request.update({
                    'optimization_score': combined_score,
                    'predicted_duration': prediction.estimated_duration,
                    'predicted_memory': prediction.predicted_memory,
                    'predicted_cpu': prediction.predicted_cpu,
                    'recommended_batch_size': prediction.recommended_batch_size,
                    'confidence': prediction.confidence,
                    'risk_factors': prediction.risk_factors
                })
                
                prioritized_requests.append(optimized_request)
            
            # Sort by optimization score (higher is better)
            prioritized_requests.sort(key=lambda x: x['optimization_score'], reverse=True)
            
            logger.info(f"Optimized schedule for {len(prioritized_requests)} import requests")
            return prioritized_requests
            
        except Exception as e:
            logger.error(f"Error optimizing import schedule: {e}")
            return import_requests
    
    def generate_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate intelligent optimization recommendations"""
        try:
            recommendations = []
            
            if len(self.performance_history) < 3:
                recommendations.append(OptimizationRecommendation(
                    category="data_collection",
                    recommendation="Continue importing to collect performance data for optimization",
                    confidence=1.0,
                    expected_improvement=0.0,
                    implementation_priority="low",
                    estimated_impact="Enables future optimizations"
                ))
                return recommendations
            
            recent_metrics = list(self.performance_history)[-10:]
            
            # Analyze performance trends
            avg_success_rate = statistics.mean([m.success_rate for m in recent_metrics])
            avg_throughput = statistics.mean([m.throughput for m in recent_metrics if m.throughput > 0])
            avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
            avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
            
            # Batch size optimization
            if len(set([m.batch_size for m in recent_metrics])) > 1:
                optimal_batch = self._find_optimal_batch_size(recent_metrics)
                if optimal_batch != self.current_batch_size:
                    improvement = abs(optimal_batch - self.current_batch_size) / self.current_batch_size * 0.1
                    recommendations.append(OptimizationRecommendation(
                        category="batch_sizing",
                        recommendation=f"Adjust batch size from {self.current_batch_size} to {optimal_batch}",
                        confidence=0.8,
                        expected_improvement=improvement,
                        implementation_priority="high",
                        estimated_impact=f"Potential {improvement*100:.1f}% throughput improvement"
                    ))
            
            # Success rate optimization
            if avg_success_rate < self.target_success_rate:
                recommendations.append(OptimizationRecommendation(
                    category="error_reduction",
                    recommendation=f"Implement error recovery mechanisms (current success rate: {avg_success_rate:.1%})",
                    confidence=0.9,
                    expected_improvement=(self.target_success_rate - avg_success_rate),
                    implementation_priority="high",
                    estimated_impact="Reduce manual intervention and improve reliability"
                ))
            
            # Memory optimization
            if avg_memory > self.max_memory_usage:
                recommendations.append(OptimizationRecommendation(
                    category="memory_optimization",
                    recommendation=f"Reduce batch size or implement memory cleanup (usage: {avg_memory:.1%})",
                    confidence=0.9,
                    expected_improvement=0.2,
                    implementation_priority="medium",
                    estimated_impact="Prevent out-of-memory errors and improve stability"
                ))
            
            # CPU optimization
            if avg_cpu > self.max_cpu_usage:
                recommendations.append(OptimizationRecommendation(
                    category="cpu_optimization",
                    recommendation=f"Implement parallel processing or reduce batch size (CPU: {avg_cpu:.1%})",
                    confidence=0.8,
                    expected_improvement=0.15,
                    implementation_priority="medium",
                    estimated_impact="Reduce processing time and system load"
                ))
            
            # Throughput optimization
            if avg_throughput < self.target_throughput:
                improvement_needed = (self.target_throughput - avg_throughput) / self.target_throughput
                recommendations.append(OptimizationRecommendation(
                    category="throughput_optimization",
                    recommendation=f"Optimize processing pipeline (current: {avg_throughput:.0f} emails/min)",
                    confidence=0.7,
                    expected_improvement=improvement_needed,
                    implementation_priority="medium",
                    estimated_impact=f"Increase throughput by {improvement_needed*100:.1f}%"
                ))
            
            # Store recommendations
            for rec in recommendations:
                self._store_optimization_recommendation(rec)
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return []
    
    def _optimize_batch_size(self):
        """Automatically optimize batch size based on performance history"""
        try:
            if len(self.performance_history) < 5:
                return
            
            # Analyze recent performance
            recent_metrics = list(self.performance_history)[-5:]
            
            # Find best performing batch size
            best_batch_size = self._find_optimal_batch_size(recent_metrics)
            
            if best_batch_size != self.current_batch_size:
                old_batch_size = self.current_batch_size
                self.current_batch_size = best_batch_size
                
                logger.info(f"Optimized batch size: {old_batch_size} → {best_batch_size}")
            
        except Exception as e:
            logger.error(f"Error optimizing batch size: {e}")
    
    def _find_optimal_batch_size(self, metrics: List[PerformanceMetrics]) -> int:
        """Find optimal batch size from performance metrics"""
        if not metrics:
            return self.current_batch_size
        
        # Score each batch size by throughput and success rate
        batch_scores = {}
        for metric in metrics:
            if metric.batch_size not in batch_scores:
                batch_scores[metric.batch_size] = []
            
            # Combined score: throughput * success_rate * memory_efficiency
            memory_efficiency = max(0.1, 1.0 - metric.memory_usage)
            score = metric.throughput * metric.success_rate * memory_efficiency
            batch_scores[metric.batch_size].append(score)
        
        # Find batch size with highest average score
        best_batch_size = self.current_batch_size
        best_score = 0
        
        for batch_size, scores in batch_scores.items():
            avg_score = statistics.mean(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_batch_size = batch_size
        
        # Ensure batch size is within bounds
        return max(self.min_batch_size, min(self.max_batch_size, best_batch_size))
    
    def _calculate_optimal_batch_size(self, email_count: int, throughput: float, 
                                    memory_usage: float, cpu_usage: float) -> int:
        """Calculate optimal batch size for given conditions"""
        # Start with current batch size
        optimal_size = self.current_batch_size
        
        # Adjust based on memory usage
        if memory_usage > 0.8:
            optimal_size = int(optimal_size * 0.7)
        elif memory_usage < 0.3:
            optimal_size = int(optimal_size * 1.3)
        
        # Adjust based on CPU usage
        if cpu_usage > 0.9:
            optimal_size = int(optimal_size * 0.8)
        elif cpu_usage < 0.4:
            optimal_size = int(optimal_size * 1.2)
        
        # Adjust for email count
        if email_count > 1000:
            optimal_size = min(optimal_size, 100)  # Smaller batches for large imports
        elif email_count < 50:
            optimal_size = min(optimal_size, email_count)  # Don't exceed email count
        
        # Ensure within bounds
        return max(self.min_batch_size, min(self.max_batch_size, optimal_size))
    
    def _check_optimization_triggers(self):
        """Check if optimization should be triggered"""
        if len(self.performance_history) < 5:
            return
        
        recent_metrics = list(self.performance_history)[-5:]
        
        # Check for performance degradation
        recent_throughput = [m.throughput for m in recent_metrics[-3:] if m.throughput > 0]
        older_throughput = [m.throughput for m in recent_metrics[:2] if m.throughput > 0]
        
        if recent_throughput and older_throughput:
            recent_avg = statistics.mean(recent_throughput)
            older_avg = statistics.mean(older_throughput)
            
            if recent_avg < older_avg * 0.8:  # 20% degradation
                logger.warning("Performance degradation detected, triggering optimization")
                self._optimize_batch_size()
        
        # Check for resource usage issues
        recent_memory = statistics.mean([m.memory_usage for m in recent_metrics])
        if recent_memory > 0.9:
            logger.warning("High memory usage detected, reducing batch size")
            self.current_batch_size = max(self.min_batch_size, int(self.current_batch_size * 0.7))
    
    def _store_performance_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        try:
            conn = sqlite3.connect(self.optimization_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics 
                (timestamp, batch_size, processing_time, memory_usage, cpu_usage, 
                 success_rate, emails_per_second, error_count, throughput)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.batch_size,
                metrics.processing_time,
                metrics.memory_usage,
                metrics.cpu_usage,
                metrics.success_rate,
                metrics.emails_per_second,
                metrics.error_count,
                metrics.throughput
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing performance metrics: {e}")
    
    def _store_optimization_recommendation(self, recommendation: OptimizationRecommendation):
        """Store optimization recommendation in database"""
        try:
            conn = sqlite3.connect(self.optimization_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO optimization_recommendations 
                (timestamp, category, recommendation, confidence, expected_improvement,
                 implementation_priority, estimated_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                recommendation.category,
                recommendation.recommendation,
                recommendation.confidence,
                recommendation.expected_improvement,
                recommendation.implementation_priority,
                recommendation.estimated_impact
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing optimization recommendation: {e}")
    
    def _store_resource_prediction(self, email_count: int, prediction: ResourcePrediction):
        """Store resource prediction for later validation"""
        try:
            conn = sqlite3.connect(self.optimization_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO resource_predictions 
                (timestamp, email_count, estimated_duration, predicted_memory, predicted_cpu,
                 recommended_batch_size, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                email_count,
                prediction.estimated_duration,
                prediction.predicted_memory,
                prediction.predicted_cpu,
                prediction.recommended_batch_size,
                prediction.confidence
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing resource prediction: {e}")
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'current_configuration': {
                    'batch_size': self.current_batch_size,
                    'optimization_interval': self.optimization_interval,
                    'performance_tracking': self.monitoring_active
                },
                'performance_statistics': {
                    'total_batches_tracked': len(self.performance_history),
                    'average_throughput': 0,
                    'average_success_rate': 0,
                    'average_memory_usage': 0,
                    'average_cpu_usage': 0
                },
                'optimization_status': {
                    'recommendations_generated': 0,
                    'optimizations_applied': self.batch_counter // self.optimization_interval,
                    'current_batch_size': self.current_batch_size
                }
            }
            
            if self.performance_history:
                recent_metrics = list(self.performance_history)
                summary['performance_statistics'].update({
                    'average_throughput': statistics.mean([m.throughput for m in recent_metrics if m.throughput > 0]),
                    'average_success_rate': statistics.mean([m.success_rate for m in recent_metrics]),
                    'average_memory_usage': statistics.mean([m.memory_usage for m in recent_metrics]),
                    'average_cpu_usage': statistics.mean([m.cpu_usage for m in recent_metrics])
                })
            
            # Get recent recommendations count
            try:
                conn = sqlite3.connect(self.optimization_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM optimization_recommendations WHERE timestamp > ?", 
                             ((datetime.now() - timedelta(hours=24)).isoformat(),))
                summary['optimization_status']['recommendations_generated'] = cursor.fetchone()[0]
                conn.close()
            except:
                pass
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating optimization summary: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

# Initialize Smart Optimizer for global use
smart_optimizer = SmartImportOptimizer()

def optimize_import_batch(email_count: int, priority: str = 'medium', 
                         characteristics: Dict[str, Any] = None) -> Dict[str, Any]:
    """Optimize a single import batch"""
    logger.info(f"Optimizing import batch: {email_count} emails, priority: {priority}")
    
    # Start performance monitoring if not active
    if not smart_optimizer.monitoring_active:
        smart_optimizer.start_performance_monitoring()
    
    # Predict performance
    prediction = smart_optimizer.predict_batch_performance(email_count, characteristics)
    
    # Generate recommendations
    recommendations = smart_optimizer.generate_optimization_recommendations()
    
    # Prepare optimization result
    result = {
        'optimized_batch_size': prediction.recommended_batch_size,
        'estimated_duration': prediction.estimated_duration,
        'predicted_resources': {
            'memory': prediction.predicted_memory,
            'cpu': prediction.predicted_cpu
        },
        'confidence': prediction.confidence,
        'risk_factors': prediction.risk_factors,
        'recommendations': [asdict(rec) for rec in recommendations],
        'optimization_applied': True
    }
    
    # Update current batch size if recommended
    if prediction.confidence > 0.7:
        smart_optimizer.current_batch_size = prediction.recommended_batch_size
    
    logger.info(f"Batch optimization completed: batch_size={prediction.recommended_batch_size}, "
               f"duration={prediction.estimated_duration:.1f}s, confidence={prediction.confidence:.1%}")
    
    return result

def track_import_performance(batch_id: str, email_count: int, success_count: int, 
                           error_count: int, duration: float) -> Dict[str, Any]:
    """Track import performance for optimization"""
    
    # Update performance tracking
    smart_optimizer.update_batch_progress(email_count, success_count, error_count)
    smart_optimizer.complete_batch_tracking(email_count, success_count, error_count)
    
    # Get optimization summary
    summary = smart_optimizer.get_optimization_summary()
    
    result = {
        'batch_id': batch_id,
        'performance_tracked': True,
        'optimization_summary': summary,
        'recommendations_available': len(smart_optimizer.generate_optimization_recommendations()) > 0
    }
    
    logger.info(f"Performance tracking completed for batch {batch_id}")
    return result

if __name__ == "__main__":
    # Example usage and testing
    logger.info("Smart Import Optimizer - Phase 4.2 Module")
    logger.info("Testing optimization capabilities...")
    
    # Start monitoring
    smart_optimizer.start_performance_monitoring()
    
    # Test batch optimization
    test_result = optimize_import_batch(
        email_count=150,
        priority='high',
        characteristics={'has_attachments': True, 'avg_size': 50000}
    )
    
    print("\n=== SMART OPTIMIZATION RESULTS ===")
    print(f"Optimized batch size: {test_result['optimized_batch_size']}")
    print(f"Estimated duration: {test_result['estimated_duration']:.1f} seconds")
    print(f"Predicted memory usage: {test_result['predicted_resources']['memory']:.1%}")
    print(f"Predicted CPU usage: {test_result['predicted_resources']['cpu']:.1%}")
    print(f"Confidence: {test_result['confidence']:.1%}")
    print(f"Risk factors: {len(test_result['risk_factors'])}")
    print(f"Recommendations: {len(test_result['recommendations'])}")
    
    # Simulate batch tracking
    batch_id = smart_optimizer.start_batch_tracking(50, 150)
    time.sleep(1)  # Simulate processing time
    
    tracking_result = track_import_performance(batch_id, 150, 145, 5, 45.0)
    
    print(f"\n=== PERFORMANCE TRACKING ===")
    print(f"Batch ID: {tracking_result['batch_id']}")
    print(f"Performance tracked: {tracking_result['performance_tracked']}")
    print(f"Recommendations available: {tracking_result['recommendations_available']}")
    
    # Stop monitoring
    smart_optimizer.stop_performance_monitoring()
    
    print("\n✅ Smart Import Optimizer Phase 4.2 testing completed successfully!") 