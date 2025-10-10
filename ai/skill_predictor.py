"""
Machine learning skill predictor using Random Forest classifier.
Analyzes player performance to predict skill level.
"""

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from config.settings import METRICS_FILE, MODEL_DIR, MIN_TRAINING_SAMPLES


class SkillPredictor:
    """
    ML-based skill level prediction using Random Forest.
    Classifies players as novice, intermediate, or expert.
    """
    
    def __init__(self):
        """Initialize skill predictor."""
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature columns for prediction
        self.feature_columns = [
            'completion_time',
            'jumps',
            'deaths',
            'coins_collected',
            'enemies_defeated',
            'total_distance',
            'precise_landings',
            'max_speed',
            'air_time_ratio',
            'completion_speed'
        ]
        
        # Ensure model directory exists
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Try to load existing model
        self.load_model()
        
        # If no model exists, create a new one
        if self.model is None:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            print("Created new Random Forest model")
    
    def load_model(self):
        """Load pre-trained model if available."""
        model_path = os.path.join(MODEL_DIR, 'skill_predictor.pkl')
        scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                print("Loaded pre-trained skill prediction model")
                return True
        except Exception as e:
            print(f"Could not load model: {e}")
        
        return False
    
    def save_model(self):
        """Save trained model to disk."""
        try:
            model_path = os.path.join(MODEL_DIR, 'skill_predictor.pkl')
            scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            print(f"Model saved to {model_path}")
            
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def train_model(self, force_retrain=False):
        """
        Train or retrain the Random Forest model.
        
        Args:
            force_retrain: Force retraining even if model exists
            
        Returns:
            True if training was successful
        """
        # Load historical data
        try:
            if not os.path.exists(METRICS_FILE):
                print("No training data available yet")
                return False
            
            df = pd.read_csv(METRICS_FILE)
            
            if len(df) < MIN_TRAINING_SAMPLES:
                print(f"Need at least {MIN_TRAINING_SAMPLES} samples to train. Current: {len(df)}")
                return False
            
            # Prepare features and labels
            X = df[self.feature_columns].values
            y = df['skill_level'].values
            
            # Handle missing values
            X = np.nan_to_num(X, nan=0.0)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            if len(df) >= 20:
                # Use train/test split if enough data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42, stratify=y
                )
                
                self.model.fit(X_train, y_train)
                
                # Evaluate
                train_score = self.model.score(X_train, y_train)
                test_score = self.model.score(X_test, y_test)
                
                print(f"Model trained - Train accuracy: {train_score:.2f}, Test accuracy: {test_score:.2f}")
            else:
                # Train on all data if limited samples
                self.model.fit(X_scaled, y)
                score = self.model.score(X_scaled, y)
                print(f"Model trained on {len(df)} samples - Accuracy: {score:.2f}")
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            # Print feature importance
            importances = self.model.feature_importances_
            feature_importance = sorted(zip(self.feature_columns, importances), 
                                       key=lambda x: x[1], reverse=True)
            
            print("\nFeature Importance:")
            for feature, importance in feature_importance[:5]:
                print(f"  {feature}: {importance:.3f}")
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def predict_skill(self, metrics_dict):
        """
        Predict player skill level from metrics.
        
        Args:
            metrics_dict: Dictionary of player metrics
            
        Returns:
            Predicted skill level: 'novice', 'intermediate', or 'expert'
        """
        # If model isn't trained yet, use heuristic
        if not self.is_trained:
            print("Model not trained yet, using heuristic prediction")
            return self._heuristic_prediction(metrics_dict)
        
        try:
            # Extract features
            features = [metrics_dict.get(col, 0) for col in self.feature_columns]
            features = np.array(features).reshape(1, -1)
            
            # Handle missing values
            features = np.nan_to_num(features, nan=0.0)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Map to class names
            classes = self.model.classes_
            prob_dict = dict(zip(classes, probabilities))
            
            print(f"\nSkill Prediction Probabilities:")
            for skill, prob in sorted(prob_dict.items(), key=lambda x: x[1], reverse=True):
                print(f"  {skill}: {prob:.2%}")
            
            return prediction
            
        except Exception as e:
            print(f"Error predicting skill: {e}")
            return self._heuristic_prediction(metrics_dict)
    
    def _heuristic_prediction(self, metrics_dict):
        """
        Fallback heuristic prediction when ML model unavailable.
        
        Args:
            metrics_dict: Dictionary of metrics
            
        Returns:
            Predicted skill level
        """
        score = 0
        
        # Fast completion
        completion_time = metrics_dict.get('completion_time', 100)
        if completion_time < 30:
            score += 3
        elif completion_time < 60:
            score += 2
        else:
            score += 1
        
        # Low deaths
        deaths = metrics_dict.get('deaths', 10)
        if deaths == 0:
            score += 3
        elif deaths <= 2:
            score += 2
        else:
            score += 1
        
        # Coin collection
        coins = metrics_dict.get('coins_collected', 0)
        if coins > 10:
            score += 2
        elif coins > 5:
            score += 1
        
        # Enemy defeats
        enemies = metrics_dict.get('enemies_defeated', 0)
        if enemies > 3:
            score += 2
        elif enemies > 1:
            score += 1
        
        # High completion speed
        completion_speed = metrics_dict.get('completion_speed', 0)
        if completion_speed > 100:
            score += 2
        elif completion_speed > 50:
            score += 1
        
        # Map score to skill
        if score >= 10:
            return 'expert'
        elif score >= 6:
            return 'intermediate'
        else:
            return 'novice'
    
    def update_incremental(self, new_metrics_dict):
        """
        Update model incrementally with new data.
        
        Args:
            new_metrics_dict: New metrics to learn from
        """
        # For Random Forest, we need to retrain on all data
        # Check if we should retrain based on number of new samples
        try:
            df = pd.read_csv(METRICS_FILE)
            
            # Retrain every N samples
            if len(df) % 5 == 0 and len(df) >= MIN_TRAINING_SAMPLES:
                print("\nRetraining model with new data...")
                self.train_model()
                
        except Exception as e:
            print(f"Error in incremental update: {e}")
