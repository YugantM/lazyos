import os
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List, Dict, Any
import logging
from collections import Counter
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserAnalyzer:
    def __init__(self):
        self.chrome_history_path = self._get_chrome_history_path()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
        
        # Define category keywords
        self.category_keywords = {
            'work': ['github', 'stackoverflow', 'gitlab', 'jira', 'confluence', 'slack', 'teams', 'zoom', 'meet', 'code', 'dev', 'development', 'programming'],
            'social': ['facebook', 'twitter', 'instagram', 'linkedin', 'reddit', 'social', 'chat', 'message'],
            'news': ['news', 'article', 'blog', 'medium', 'times', 'post', 'daily'],
            'entertainment': ['youtube', 'netflix', 'spotify', 'music', 'video', 'game', 'play'],
            'shopping': ['amazon', 'shop', 'store', 'cart', 'buy', 'purchase', 'market'],
            'learning': ['course', 'learn', 'tutorial', 'study', 'education', 'school', 'university', 'college'],
            'productivity': ['todo', 'task', 'note', 'calendar', 'schedule', 'plan', 'organize']
        }
        
        # Time-based patterns
        self.time_patterns = {
            'morning': (5, 12),    # 5 AM to 12 PM
            'afternoon': (12, 17), # 12 PM to 5 PM
            'evening': (17, 22),   # 5 PM to 10 PM
            'night': (22, 5)       # 10 PM to 5 AM
        }

    def _get_chrome_history_path(self) -> str:
        """Get the path to Chrome's history database."""
        if os.name == 'nt':  # Windows
            return os.path.join(os.environ['LOCALAPPDATA'], 
                              'Google', 'Chrome', 'User Data', 'Default', 'History')
        elif os.name == 'posix':  # macOS or Linux
            if os.path.exists(os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History')):
                return os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History')
            else:
                return os.path.expanduser('~/.config/google-chrome/Default/History')
        else:
            raise OSError("Unsupported operating system")

    def get_browser_history(self, days: int = None) -> pd.DataFrame:
        """Extract browser history from Chrome's SQLite database."""
        try:
            # Create a copy of the history file (as it might be locked by Chrome)
            temp_history = 'temp_history'
            with open(self.chrome_history_path, 'rb') as f:
                with open(temp_history, 'wb') as f2:
                    f2.write(f.read())

            # Connect to the temporary database
            conn = sqlite3.connect(temp_history)
            
            # Query to get all history
            query = """
            SELECT url, title, last_visit_time, visit_count
            FROM urls
            ORDER BY last_visit_time DESC
            """
            
            # Read into DataFrame
            df = pd.read_sql_query(query, conn)
            
            # Clean up
            conn.close()
            os.remove(temp_history)
            
            return df
            
        except Exception as e:
            logger.error(f"Error accessing browser history: {e}")
            return pd.DataFrame()

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the browser history data."""
        if df.empty:
            return df
            
        # Convert Chrome's timestamp (microseconds since 1601-01-01) to Unix timestamp
        # Chrome's epoch is 1601-01-01, Unix epoch is 1970-01-01
        # Difference in microseconds: (1970-1601) * 365.25 * 24 * 60 * 60 * 1000000
        CHROME_EPOCH_DIFF = 11644473600000000
        
        try:
            # Convert to Unix timestamp (seconds since 1970)
            df['last_visit_time'] = pd.to_numeric(df['last_visit_time'], errors='coerce')
            df['last_visit_time'] = (df['last_visit_time'] - CHROME_EPOCH_DIFF) / 1000000
            
            # Filter out any invalid timestamps
            df = df[df['last_visit_time'] > 0]
            
            # Convert to datetime
            df['last_visit_time'] = pd.to_datetime(df['last_visit_time'], unit='s', errors='coerce')
            
            # Drop rows with invalid timestamps
            df = df.dropna(subset=['last_visit_time'])
            
            # Extract domain from URL
            df['domain'] = df['url'].apply(lambda x: x.split('/')[2] if len(x.split('/')) > 2 else x)
            
            # Create features
            df['hour'] = df['last_visit_time'].dt.hour
            df['day_of_week'] = df['last_visit_time'].dt.dayofweek
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing timestamps: {e}")
            return pd.DataFrame()

    def cluster_tabs(self, df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
        """Cluster tabs based on their content and usage patterns."""
        if df.empty:
            return df
            
        # Prepare text features
        text_features = self.vectorizer.fit_transform(df['title'].fillna('') + ' ' + df['url'].fillna(''))
        
        # Prepare numerical features
        numerical_features = df[['visit_count', 'hour', 'day_of_week']].values
        numerical_features = self.scaler.fit_transform(numerical_features)
        
        # Combine features
        combined_features = np.hstack([text_features.toarray(), numerical_features])
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['cluster'] = kmeans.fit_predict(combined_features)
        
        return df

    def _get_time_of_day(self, hour: int) -> str:
        """Determine time of day based on hour."""
        for period, (start, end) in self.time_patterns.items():
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                return period
        return 'unknown'

    def _get_category_scores(self, text: str) -> Dict[str, float]:
        """Calculate category scores for a given text."""
        text = text.lower()
        scores = {category: 0.0 for category in self.category_keywords.keys()}
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores

    def _get_dominant_category(self, cluster_data: pd.DataFrame) -> str:
        """Determine the dominant category for a cluster."""
        all_text = ' '.join(cluster_data['title'].fillna('') + ' ' + cluster_data['url'].fillna(''))
        scores = self._get_category_scores(all_text)
        return max(scores.items(), key=lambda x: x[1])[0]

    def _get_time_pattern(self, cluster_data: pd.DataFrame) -> str:
        """Determine the dominant time pattern for a cluster."""
        time_counts = Counter(cluster_data['hour'].apply(self._get_time_of_day))
        return time_counts.most_common(1)[0][0]

    def _generate_mode_name(self, cluster_data: pd.DataFrame, cluster: int) -> str:
        """Generate a meaningful name for the mode based on cluster content."""
        category = self._get_dominant_category(cluster_data)
        time_pattern = self._get_time_pattern(cluster_data)
        
        # Get top domain for additional context
        top_domain = cluster_data['domain'].value_counts().head(1).index[0]
        domain_name = re.sub(r'[^a-zA-Z]', '', top_domain.split('.')[0])
        
        # Generate name based on patterns
        if category == 'work':
            if time_pattern in ['morning', 'afternoon']:
                return f"work_{time_pattern}"
            else:
                return f"work_{domain_name}"
        elif category == 'social':
            return f"social_{time_pattern}"
        elif category == 'entertainment':
            return f"fun_{time_pattern}"
        else:
            return f"{category}_{domain_name}"

    def _generate_mode_description(self, cluster_data: pd.DataFrame, mode_name: str) -> str:
        """Generate a detailed description for the mode."""
        category = self._get_dominant_category(cluster_data)
        time_pattern = self._get_time_pattern(cluster_data)
        
        # Get top domains and their visit counts
        top_domains = cluster_data['domain'].value_counts().head(3)
        domain_info = ', '.join([f"{domain} ({count} visits)" for domain, count in top_domains.items()])
        
        # Get average visit time
        avg_hour = cluster_data['hour'].mean()
        time_str = datetime.strptime(f"{int(avg_hour):02d}:00", "%H:%M").strftime("%I:%M %p")
        
        description = f"Auto-generated {category} mode for {time_pattern} usage. "
        description += f"Most active around {time_str}. "
        description += f"Top sites: {domain_info}."
        
        return description

    def generate_modes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate modes based on clustered data with meaningful names and descriptions."""
        if df.empty:
            return {}
            
        modes = {}
        
        for cluster in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster]
            
            # Get most common URLs
            top_urls = cluster_data['url'].value_counts().head(5).index.tolist()
            
            # Generate mode name and description
            mode_name = self._generate_mode_name(cluster_data, cluster)
            description = self._generate_mode_description(cluster_data, mode_name)
            
            # Create mode configuration
            modes[mode_name] = {
                "apps": [],  # Could be populated based on domain patterns
                "tabs": top_urls,
                "comment": description
            }
            
        return modes

    def update_modes_json(self, modes: Dict[str, Any], config_path: str):
        """Update the modes.json file with new modes."""
        try:
            # Read existing modes
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    existing_modes = json.load(f)
            else:
                existing_modes = {}
            
            # Update with new modes
            existing_modes.update(modes)
            
            # Write back to file
            with open(config_path, 'w') as f:
                json.dump(existing_modes, f, indent=2)
                
            logger.info(f"Successfully updated modes.json with {len(modes)} new modes")
            
        except Exception as e:
            logger.error(f"Error updating modes.json: {e}")

def main():
    """Main function to run the browser analysis and mode generation."""
    analyzer = BrowserAnalyzer()
    
    # Get browser history
    history_df = analyzer.get_browser_history(days=None)
    
    if not history_df.empty:
        # Preprocess data
        processed_df = analyzer.preprocess_data(history_df)
        
        # Cluster tabs
        clustered_df = analyzer.cluster_tabs(processed_df)
        
        # Generate modes
        modes = analyzer.generate_modes(clustered_df)
        
        # Update modes.json
        config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'modes.json')
        analyzer.update_modes_json(modes, config_path)
    else:
        logger.warning("No browser history data found")

if __name__ == "__main__":
    main() 