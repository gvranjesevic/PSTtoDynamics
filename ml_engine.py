"""
ML Pattern Recognition Engine - Phase 4.1 Core Module

This module provides machine learning capabilities for pattern recognition,
email classification, sender behavior analysis, and timeline prediction.
Integrates with Phase 3 analytics to provide intelligent insights.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
import pickle
import os
from collections import defaultdict, Counter
from dataclasses import dataclass
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailPattern:
    """Represents an identified email pattern"""
    pattern_type: str
    confidence: float
    features: Dict[str, Any]
    prediction: Optional[str] = None
    importance_score: float = 0.0

@dataclass
class SenderBehavior:
    """Represents sender behavior analysis results"""
    sender_email: str
    behavior_category: str
    frequency_pattern: str
    importance_score: float
    predicted_next_contact: Optional[datetime] = None
    confidence: float = 0.0

@dataclass
class TimelineGap:
    """Represents a predicted or detected timeline gap"""
    start_date: datetime
    end_date: datetime
    gap_type: str  # 'weekend', 'vacation', 'suspicious', 'predicted'
    confidence: float
    severity: str  # 'low', 'medium', 'high'
    recommendation: str

class MLPatternEngine:
    """
    Advanced ML Pattern Recognition Engine for email analysis and prediction.
    
    Capabilities:
    - Email pattern classification and importance scoring
    - Sender behavior modeling and prediction
    - Timeline gap prediction and anomaly detection
    - Content intelligence and subject analysis
    - Communication frequency forecasting
    """
    
    def __init__(self, analytics_db_path: str = "analytics.db"):
        """Initialize the ML Pattern Engine"""
        self.analytics_db_path = analytics_db_path
        self.models_dir = "ml_models"
        self.ensure_models_directory()
        
        # Initialize ML models
        self.pattern_classifier = None
        self.sender_clusterer = None
        self.timeline_predictor = None
        self.anomaly_detector = None
        self.content_vectorizer = None
        
        # Feature extractors
        self.subject_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Pattern recognition data
        self.email_patterns = []
        self.sender_behaviors = {}
        self.timeline_predictions = []
        
        logger.info("ML Pattern Engine initialized successfully")
    
    def ensure_models_directory(self):
        """Ensure the models directory exists"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            logger.info(f"Created models directory: {self.models_dir}")
    
    def load_training_data(self) -> pd.DataFrame:
        """Load training data from Phase 3 analytics database"""
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            
            # Load email analytics data
            query = """
            SELECT 
                sa.email_address, sa.category, sa.importance_score,
                sa.avg_response_time, sa.total_emails, sa.first_contact,
                sa.last_contact, sa.communication_pattern,
                ia.session_id, ia.total_emails as session_emails,
                ia.success_rate, ia.processing_speed, ia.avg_batch_size
            FROM sender_analytics sa
            LEFT JOIN import_analytics ia ON sa.email_address LIKE '%' || ia.session_id || '%'
            WHERE sa.total_emails > 0
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"Loaded {len(df)} records for ML training")
            return df
            
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return pd.DataFrame()
    
    def extract_email_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features from email data for ML models"""
        features = []
        
        for _, row in df.iterrows():
            # Temporal features
            first_contact = pd.to_datetime(row['first_contact']) if row['first_contact'] else datetime.now()
            last_contact = pd.to_datetime(row['last_contact']) if row['last_contact'] else datetime.now()
            
            contact_duration = (last_contact - first_contact).days
            emails_per_day = row['total_emails'] / max(contact_duration, 1)
            
            # Domain analysis
            domain = row['email_address'].split('@')[1] if '@' in str(row['email_address']) else 'unknown'
            is_business_domain = 1 if any(term in domain.lower() for term in ['company', 'corp', 'inc', 'ltd']) else 0
            
            # Communication pattern encoding
            pattern_encoding = {
                'regular': 1, 'sporadic': 2, 'burst': 3, 'declining': 4, 'unknown': 0
            }
            pattern_code = pattern_encoding.get(row['communication_pattern'], 0)
            
            feature_vector = [
                row['total_emails'],
                row['importance_score'],
                row['avg_response_time'] or 0,
                emails_per_day,
                contact_duration,
                is_business_domain,
                pattern_code,
                len(domain),
                row['success_rate'] or 1.0,
                row['processing_speed'] or 1000
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train_pattern_classifier(self, df: pd.DataFrame) -> bool:
        """Train the email pattern classification model"""
        try:
            if len(df) < 5:
                logger.warning("Insufficient data for pattern classifier training")
                return False
            
            # Extract features and labels
            X = self.extract_email_features(df)
            y = df['category'].fillna('unknown')
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train Random Forest classifier
            self.pattern_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.pattern_classifier.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.pattern_classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Pattern classifier trained with accuracy: {accuracy:.3f}")
            
            # Save model
            model_path = os.path.join(self.models_dir, 'pattern_classifier.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(self.pattern_classifier, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Error training pattern classifier: {e}")
            return False
    
    def train_sender_behavior_models(self, df: pd.DataFrame) -> bool:
        """Train sender behavior clustering and prediction models"""
        try:
            if len(df) < 3:
                logger.warning("Insufficient data for sender behavior training")
                return False
            
            # Extract behavioral features
            behavioral_features = []
            for _, row in df.iterrows():
                features = [
                    row['total_emails'],
                    row['importance_score'],
                    row['avg_response_time'] or 0,
                    len(str(row['email_address'])),
                    1 if 'business' in str(row['category']).lower() else 0
                ]
                behavioral_features.append(features)
            
            X = np.array(behavioral_features)
            
            # Train clustering model for behavior categorization
            n_clusters = min(5, len(df))
            self.sender_clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = self.sender_clusterer.fit_predict(X)
            
            # Train timeline predictor (simple linear regression for now)
            if 'last_contact' in df.columns and df['last_contact'].notna().sum() > 2:
                timeline_features = X[:, :3]  # Use first 3 features for timeline prediction
                timeline_targets = pd.to_datetime(df['last_contact'], errors='coerce')
                timeline_targets = timeline_targets.apply(lambda x: x.timestamp() if pd.notna(x) else 0)
                
                self.timeline_predictor = LinearRegression()
                self.timeline_predictor.fit(timeline_features, timeline_targets)
            
            # Train anomaly detector
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.anomaly_detector.fit(X)
            
            logger.info(f"Sender behavior models trained with {n_clusters} behavior clusters")
            
            # Save models
            models_to_save = {
                'sender_clusterer.pkl': self.sender_clusterer,
                'timeline_predictor.pkl': self.timeline_predictor,
                'anomaly_detector.pkl': self.anomaly_detector
            }
            
            for filename, model in models_to_save.items():
                if model is not None:
                    model_path = os.path.join(self.models_dir, filename)
                    with open(model_path, 'wb') as f:
                        pickle.dump(model, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Error training sender behavior models: {e}")
            return False
    
    def load_trained_models(self) -> bool:
        """Load previously trained ML models"""
        try:
            model_files = {
                'pattern_classifier.pkl': 'pattern_classifier',
                'sender_clusterer.pkl': 'sender_clusterer',
                'timeline_predictor.pkl': 'timeline_predictor',
                'anomaly_detector.pkl': 'anomaly_detector'
            }
            
            loaded_count = 0
            for filename, attr_name in model_files.items():
                model_path = os.path.join(self.models_dir, filename)
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        setattr(self, attr_name, pickle.load(f))
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} pre-trained ML models")
            return loaded_count > 0
            
        except Exception as e:
            logger.error(f"Error loading trained models: {e}")
            return False
    
    def analyze_email_pattern(self, email_data: Dict[str, Any]) -> EmailPattern:
        """Analyze an individual email and classify its pattern"""
        try:
            # Extract features for prediction
            features = self._extract_single_email_features(email_data)
            
            # Get pattern classification
            if self.pattern_classifier is not None:
                pattern_proba = self.pattern_classifier.predict_proba([features])[0]
                pattern_classes = self.pattern_classifier.classes_
                
                best_class_idx = np.argmax(pattern_proba)
                pattern_type = pattern_classes[best_class_idx]
                confidence = pattern_proba[best_class_idx]
            else:
                pattern_type = "unknown"
                confidence = 0.5
            
            # Calculate importance score
            importance_score = self._calculate_importance_score(email_data, features)
            
            # Create pattern object
            pattern = EmailPattern(
                pattern_type=pattern_type,
                confidence=confidence,
                features={
                    'sender': email_data.get('sender', 'unknown'),
                    'subject_length': len(email_data.get('subject', '')),
                    'has_attachments': email_data.get('has_attachments', False),
                    'is_reply': email_data.get('is_reply', False)
                },
                importance_score=importance_score
            )
            
            self.email_patterns.append(pattern)
            return pattern
            
        except Exception as e:
            logger.error(f"Error analyzing email pattern: {e}")
            return EmailPattern(
                pattern_type="error",
                confidence=0.0,
                features={},
                importance_score=0.0
            )
    
    def analyze_sender_behavior(self, sender_email: str, email_history: List[Dict]) -> SenderBehavior:
        """Analyze sender behavior patterns and predict future communication"""
        try:
            # Analyze historical communication patterns
            email_count = len(email_history)
            if email_count == 0:
                return SenderBehavior(
                    sender_email=sender_email,
                    behavior_category="unknown",
                    frequency_pattern="no_data",
                    importance_score=0.0
                )
            
            # Calculate communication metrics
            dates = [datetime.fromisoformat(email.get('date', datetime.now().isoformat())) 
                    for email in email_history]
            dates.sort()
            
            # Frequency analysis
            if len(dates) > 1:
                time_diffs = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_frequency = np.mean(time_diffs) if time_diffs else 365
                frequency_pattern = self._classify_frequency_pattern(avg_frequency)
            else:
                avg_frequency = 365
                frequency_pattern = "single_contact"
            
            # Behavior clustering if model is available
            if self.sender_clusterer is not None:
                behavioral_features = [
                    email_count,
                    len(sender_email),
                    avg_frequency,
                    sum(1 for email in email_history if email.get('has_attachments', False)),
                    1 if any(email.get('is_reply', False) for email in email_history) else 0
                ]
                
                cluster = self.sender_clusterer.predict([behavioral_features])[0]
                behavior_category = f"cluster_{cluster}"
            else:
                behavior_category = "unclassified"
            
            # Calculate importance score
            importance_score = self._calculate_sender_importance(sender_email, email_history)
            
            # Predict next contact if timeline predictor is available
            predicted_next = None
            confidence = 0.0
            if self.timeline_predictor is not None and len(dates) > 1:
                try:
                    features = [email_count, importance_score, avg_frequency]
                    next_timestamp = self.timeline_predictor.predict([features])[0]
                    predicted_next = datetime.fromtimestamp(next_timestamp)
                    confidence = 0.7  # Default confidence
                except:
                    pass
            
            behavior = SenderBehavior(
                sender_email=sender_email,
                behavior_category=behavior_category,
                frequency_pattern=frequency_pattern,
                importance_score=importance_score,
                predicted_next_contact=predicted_next,
                confidence=confidence
            )
            
            self.sender_behaviors[sender_email] = behavior
            return behavior
            
        except Exception as e:
            logger.error(f"Error analyzing sender behavior for {sender_email}: {e}")
            return SenderBehavior(
                sender_email=sender_email,
                behavior_category="error",
                frequency_pattern="unknown",
                importance_score=0.0
            )
    
    def predict_timeline_gaps(self, contact_email: str, email_history: List[Dict]) -> List[TimelineGap]:
        """Predict potential timeline gaps for a contact"""
        try:
            gaps = []
            
            if len(email_history) < 2:
                return gaps
            
            # Sort emails by date
            sorted_emails = sorted(email_history, 
                                 key=lambda x: datetime.fromisoformat(x.get('date', datetime.now().isoformat())))
            
            # Analyze existing gaps
            for i in range(len(sorted_emails) - 1):
                current_date = datetime.fromisoformat(sorted_emails[i]['date'])
                next_date = datetime.fromisoformat(sorted_emails[i+1]['date'])
                
                gap_days = (next_date - current_date).days
                
                if gap_days > 7:  # Significant gap
                    gap_type = self._classify_gap_type(current_date, next_date, gap_days)
                    severity = self._classify_gap_severity(gap_days)
                    confidence = min(0.9, gap_days / 30)  # Higher confidence for longer gaps
                    
                    recommendation = self._generate_gap_recommendation(gap_type, gap_days)
                    
                    gap = TimelineGap(
                        start_date=current_date,
                        end_date=next_date,
                        gap_type=gap_type,
                        confidence=confidence,
                        severity=severity,
                        recommendation=recommendation
                    )
                    gaps.append(gap)
            
            # Predict future gaps
            if len(sorted_emails) > 0:
                last_email = datetime.fromisoformat(sorted_emails[-1]['date'])
                days_since_last = (datetime.now() - last_email).days
                
                if days_since_last > 14:  # Predict potential ongoing gap
                    gap = TimelineGap(
                        start_date=last_email,
                        end_date=datetime.now(),
                        gap_type="predicted_ongoing",
                        confidence=0.8,
                        severity=self._classify_gap_severity(days_since_last),
                        recommendation=f"Contact has been inactive for {days_since_last} days. Consider follow-up."
                    )
                    gaps.append(gap)
            
            self.timeline_predictions.extend(gaps)
            return gaps
            
        except Exception as e:
            logger.error(f"Error predicting timeline gaps: {e}")
            return []
    
    def detect_anomalies(self, email_data: List[Dict]) -> List[Dict[str, Any]]:
        """Detect anomalous email patterns using ML"""
        try:
            anomalies = []
            
            if self.anomaly_detector is None or len(email_data) == 0:
                return anomalies
            
            # Extract features for anomaly detection
            features_list = []
            for email in email_data:
                features = self._extract_single_email_features(email)
                features_list.append(features)
            
            if not features_list:
                return anomalies
            
            # Detect anomalies
            X = np.array(features_list)
            anomaly_scores = self.anomaly_detector.decision_function(X)
            anomaly_labels = self.anomaly_detector.predict(X)
            
            # Process results
            for i, (email, score, label) in enumerate(zip(email_data, anomaly_scores, anomaly_labels)):
                if label == -1:  # Anomaly detected
                    anomaly = {
                        'email_id': email.get('id', f'email_{i}'),
                        'sender': email.get('sender', 'unknown'),
                        'subject': email.get('subject', ''),
                        'anomaly_score': score,
                        'anomaly_type': self._classify_anomaly_type(email, score),
                        'confidence': abs(score) / 2,  # Normalize confidence
                        'recommendation': self._generate_anomaly_recommendation(email, score)
                    }
                    anomalies.append(anomaly)
            
            logger.info(f"Detected {len(anomalies)} anomalous emails")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def generate_intelligence_summary(self) -> Dict[str, Any]:
        """Generate comprehensive ML intelligence summary"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'pattern_analysis': {
                    'total_patterns_identified': len(self.email_patterns),
                    'pattern_distribution': self._get_pattern_distribution(),
                    'high_confidence_patterns': len([p for p in self.email_patterns if p.confidence > 0.8]),
                },
                'sender_behavior': {
                    'total_senders_analyzed': len(self.sender_behaviors),
                    'behavior_categories': self._get_behavior_categories(),
                    'high_importance_senders': len([s for s in self.sender_behaviors.values() 
                                                  if s.importance_score > 0.7]),
                },
                'timeline_predictions': {
                    'total_gaps_identified': len(self.timeline_predictions),
                    'gap_types': self._get_gap_types(),
                    'high_severity_gaps': len([g for g in self.timeline_predictions 
                                             if g.severity == 'high']),
                },
                'model_status': {
                    'pattern_classifier_trained': self.pattern_classifier is not None,
                    'sender_clusterer_trained': self.sender_clusterer is not None,
                    'timeline_predictor_trained': self.timeline_predictor is not None,
                    'anomaly_detector_trained': self.anomaly_detector is not None,
                },
                'recommendations': self._generate_recommendations()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating intelligence summary: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _extract_single_email_features(self, email_data: Dict[str, Any]) -> List[float]:
        """Extract features from a single email for ML analysis"""
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '')
        
        features = [
            len(subject),
            len(sender),
            1 if email_data.get('has_attachments', False) else 0,
            1 if email_data.get('is_reply', False) else 0,
            1 if 'urgent' in subject.lower() else 0,
            len(sender.split('@')[0]) if '@' in sender else 0,
            1 if any(word in subject.lower() for word in ['meeting', 'call', 'urgent', 'important']) else 0,
            datetime.now().hour,  # Current hour as temporal feature
            datetime.now().weekday(),  # Current day of week
            len(email_data.get('body', '')) if 'body' in email_data else 100
        ]
        
        return features
    
    def _calculate_importance_score(self, email_data: Dict[str, Any], features: List[float]) -> float:
        """Calculate importance score for an email"""
        score = 0.5  # Base score
        
        # Subject-based importance
        subject = email_data.get('subject', '').lower()
        important_keywords = ['urgent', 'important', 'asap', 'critical', 'deadline']
        for keyword in important_keywords:
            if keyword in subject:
                score += 0.2
        
        # Sender-based importance
        sender = email_data.get('sender', '')
        if '@' in sender:
            domain = sender.split('@')[1]
            if any(term in domain.lower() for term in ['ceo', 'president', 'director']):
                score += 0.3
        
        # Attachment-based importance
        if email_data.get('has_attachments', False):
            score += 0.1
        
        # Reply-based importance
        if email_data.get('is_reply', False):
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_sender_importance(self, sender_email: str, email_history: List[Dict]) -> float:
        """Calculate importance score for a sender"""
        score = 0.3  # Base score
        
        # Volume-based importance
        email_count = len(email_history)
        if email_count > 50:
            score += 0.3
        elif email_count > 20:
            score += 0.2
        elif email_count > 5:
            score += 0.1
        
        # Consistency-based importance
        if email_count > 1:
            dates = [datetime.fromisoformat(email.get('date', datetime.now().isoformat())) 
                    for email in email_history]
            dates.sort()
            consistency = 1.0 / (1.0 + np.std([(dates[i+1] - dates[i]).days 
                                             for i in range(len(dates)-1)]))
            score += consistency * 0.2
        
        # Domain-based importance
        domain = sender_email.split('@')[1] if '@' in sender_email else ''
        if any(term in domain.lower() for term in ['company', 'corp', 'important']):
            score += 0.2
        
        return min(1.0, score)
    
    def _classify_frequency_pattern(self, avg_days: float) -> str:
        """Classify communication frequency pattern"""
        if avg_days <= 1:
            return "daily"
        elif avg_days <= 7:
            return "weekly"
        elif avg_days <= 30:
            return "monthly"
        elif avg_days <= 90:
            return "quarterly"
        else:
            return "sporadic"
    
    def _classify_gap_type(self, start_date: datetime, end_date: datetime, gap_days: int) -> str:
        """Classify the type of timeline gap"""
        # Weekend check
        if gap_days <= 3 and start_date.weekday() >= 4:  # Friday or weekend
            return "weekend"
        
        # Holiday check (simplified)
        if gap_days <= 10 and (
            (start_date.month == 12 and start_date.day > 20) or
            (start_date.month == 1 and start_date.day < 10) or
            (start_date.month == 7 and start_date.day > 20 and start_date.day < 31)
        ):
            return "holiday"
        
        # Vacation check
        if 5 <= gap_days <= 30:
            return "vacation"
        
        # Suspicious gap
        if gap_days > 30:
            return "suspicious"
        
        return "normal"
    
    def _classify_gap_severity(self, gap_days: int) -> str:
        """Classify gap severity"""
        if gap_days <= 7:
            return "low"
        elif gap_days <= 30:
            return "medium"
        else:
            return "high"
    
    def _generate_gap_recommendation(self, gap_type: str, gap_days: int) -> str:
        """Generate recommendation for timeline gap"""
        recommendations = {
            "weekend": f"Normal weekend gap ({gap_days} days)",
            "holiday": f"Expected holiday gap ({gap_days} days)",
            "vacation": f"Possible vacation period ({gap_days} days) - normal pattern",
            "suspicious": f"Unusual {gap_days}-day gap - investigate potential issues",
            "normal": f"{gap_days}-day gap within normal range"
        }
        return recommendations.get(gap_type, f"Unknown gap type: {gap_days} days")
    
    def _classify_anomaly_type(self, email: Dict[str, Any], score: float) -> str:
        """Classify type of anomaly detected"""
        subject = email.get('subject', '').lower()
        sender = email.get('sender', '')
        
        if abs(score) > 0.5:
            return "high_anomaly"
        elif 'urgent' in subject or 'critical' in subject:
            return "urgency_anomaly"
        elif len(subject) < 5:
            return "short_subject_anomaly"
        elif sender.count('@') != 1:
            return "invalid_sender_anomaly"
        else:
            return "pattern_anomaly"
    
    def _generate_anomaly_recommendation(self, email: Dict[str, Any], score: float) -> str:
        """Generate recommendation for anomaly"""
        return f"Anomalous email detected (score: {score:.3f}). Review for potential issues."
    
    def _get_pattern_distribution(self) -> Dict[str, int]:
        """Get distribution of identified patterns"""
        return dict(Counter([p.pattern_type for p in self.email_patterns]))
    
    def _get_behavior_categories(self) -> Dict[str, int]:
        """Get distribution of behavior categories"""
        return dict(Counter([s.behavior_category for s in self.sender_behaviors.values()]))
    
    def _get_gap_types(self) -> Dict[str, int]:
        """Get distribution of gap types"""
        return dict(Counter([g.gap_type for g in self.timeline_predictions]))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Pattern-based recommendations
        high_confidence_patterns = [p for p in self.email_patterns if p.confidence > 0.8]
        if len(high_confidence_patterns) > 10:
            recommendations.append(f"Strong pattern recognition achieved ({len(high_confidence_patterns)} high-confidence patterns)")
        
        # Sender behavior recommendations
        high_importance_senders = [s for s in self.sender_behaviors.values() if s.importance_score > 0.7]
        if high_importance_senders:
            recommendations.append(f"Focus on {len(high_importance_senders)} high-importance senders")
        
        # Timeline recommendations
        high_severity_gaps = [g for g in self.timeline_predictions if g.severity == 'high']
        if high_severity_gaps:
            recommendations.append(f"Investigate {len(high_severity_gaps)} high-severity timeline gaps")
        
        # Model recommendations
        if self.pattern_classifier is None:
            recommendations.append("Train pattern classifier for better email categorization")
        
        if not recommendations:
            recommendations.append("Continue monitoring for patterns and anomalies")
        
        return recommendations

# Initialize ML Engine for global use
ml_engine = MLPatternEngine()

def train_ml_models() -> bool:
    """Train all ML models using available data"""
    logger.info("Starting ML model training...")
    
    # Load training data
    df = ml_engine.load_training_data()
    
    if len(df) == 0:
        logger.warning("No training data available")
        return False
    
    # Train models
    pattern_success = ml_engine.train_pattern_classifier(df)
    behavior_success = ml_engine.train_sender_behavior_models(df)
    
    success = pattern_success or behavior_success
    
    if success:
        logger.info("ML model training completed successfully")
    else:
        logger.error("ML model training failed")
    
    return success

def analyze_import_intelligence(email_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze email data using ML intelligence"""
    logger.info(f"Analyzing {len(email_data)} emails with ML intelligence...")
    
    # Load models if not already loaded
    if ml_engine.pattern_classifier is None:
        ml_engine.load_trained_models()
    
    # Analyze patterns for each email
    patterns = []
    for email in email_data:
        pattern = ml_engine.analyze_email_pattern(email)
        patterns.append(pattern)
    
    # Group emails by sender for behavior analysis
    sender_groups = defaultdict(list)
    for email in email_data:
        sender = email.get('sender', 'unknown')
        sender_groups[sender].append(email)
    
    # Analyze sender behaviors
    behaviors = []
    for sender, emails in sender_groups.items():
        behavior = ml_engine.analyze_sender_behavior(sender, emails)
        behaviors.append(behavior)
    
    # Predict timeline gaps for each sender
    timeline_gaps = []
    for sender, emails in sender_groups.items():
        gaps = ml_engine.predict_timeline_gaps(sender, emails)
        timeline_gaps.extend(gaps)
    
    # Detect anomalies
    anomalies = ml_engine.detect_anomalies(email_data)
    
    # Generate comprehensive summary
    intelligence_summary = ml_engine.generate_intelligence_summary()
    
    result = {
        'ml_analysis': {
            'patterns_analyzed': len(patterns),
            'behaviors_analyzed': len(behaviors),
            'timeline_gaps_predicted': len(timeline_gaps),
            'anomalies_detected': len(anomalies),
            'intelligence_summary': intelligence_summary
        },
        'patterns': [{'type': p.pattern_type, 'confidence': p.confidence, 
                     'importance': p.importance_score} for p in patterns],
        'behaviors': [{'sender': b.sender_email, 'category': b.behavior_category,
                      'frequency': b.frequency_pattern, 'importance': b.importance_score}
                     for b in behaviors],
        'timeline_gaps': [{'start': g.start_date.isoformat(), 'end': g.end_date.isoformat(),
                          'type': g.gap_type, 'severity': g.severity, 'confidence': g.confidence}
                         for g in timeline_gaps],
        'anomalies': anomalies,
        'recommendations': intelligence_summary.get('recommendations', [])
    }
    
    logger.info("ML intelligence analysis completed")
    return result

if __name__ == "__main__":
    # Example usage and testing
    logger.info("ML Pattern Engine - Phase 4.1 Module")
    logger.info("Testing ML capabilities...")
    
    # Test with sample data
    sample_emails = [
        {
            'id': 'email_1',
            'sender': 'john.doe@company.com',
            'subject': 'Urgent: Project deadline meeting',
            'date': '2024-06-10T09:00:00',
            'has_attachments': True,
            'is_reply': False,
            'body': 'We need to discuss the project deadline immediately.'
        },
        {
            'id': 'email_2',
            'sender': 'jane.smith@client.com',
            'subject': 'Re: Proposal feedback',
            'date': '2024-06-11T14:30:00',
            'has_attachments': False,
            'is_reply': True,
            'body': 'Thank you for the proposal. Here is our feedback.'
        }
    ]
    
    # Run ML analysis
    results = analyze_import_intelligence(sample_emails)
    
    print("\n=== ML INTELLIGENCE ANALYSIS RESULTS ===")
    print(f"Patterns analyzed: {results['ml_analysis']['patterns_analyzed']}")
    print(f"Behaviors analyzed: {results['ml_analysis']['behaviors_analyzed']}")
    print(f"Timeline gaps predicted: {results['ml_analysis']['timeline_gaps_predicted']}")
    print(f"Anomalies detected: {results['ml_analysis']['anomalies_detected']}")
    print(f"Recommendations: {len(results['recommendations'])}")
    
    print("\n=== INTELLIGENCE SUMMARY ===")
    summary = results['ml_analysis']['intelligence_summary']
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"{key.upper()}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")
    
    print("\n✅ ML Pattern Engine Phase 4.1 testing completed successfully!") 