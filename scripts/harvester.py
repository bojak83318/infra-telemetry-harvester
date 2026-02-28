#!/usr/bin/env python3
"""
Infra Telemetry Harvester
Automated monitoring of infrastructure-related community incident reports for SRE audit.

Architecture: Low-Velocity, High-Precision Design
- Official Rate Limit Compliance via PRAW
- Read-Only Scope (Machine-to-Machine authentication)
- 15-30 minute polling intervals
"""

import os
import praw
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import time

# Configure logging with structured format for SRE monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('harvester.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('InfraTelemetryHarvester')


@dataclass
class TelemetryRecord:
    """Structured record for infrastructure telemetry data."""
    id: str
    subreddit: str
    title: str
    author: str
    created_utc: float
    url: str
    selftext: str
    score: int
    num_comments: int
    permalink: str
    harvested_at: str


class RedditTelemetryHarvester:
    """
    Responsible Builder Policy compliant Reddit harvester.
    
    Key architectural decisions:
    1. Custom User-Agent identifying as enterprise monitoring tool
    2. Read-only scope (no user impersonation)
    3. PRAW's built-in rate limit compliance
    4. Targeted subreddit list for clean researcher profile
    """
    
    # Professional User-Agent signaling enterprise infrastructure
    USER_AGENT = (
        "InfraTelemetryHarvester/1.0 "
        "(Enterprise SRE Monitoring; "
        "Contact: sre-team@company.internal; "
        "Purpose: Infrastructure Incident Research)"
    )
    
    # Targeted subreddits - keeping scope focused on infrastructure/technical
    TARGET_SUBREDDITS = [
        "GoogleCloud",
        "aws",
        "Azure",
        "devops",
        "kubernetes",
        "sysadmin",
        "SRE",
        "ClaudeAI",
        "OpenAI",
        "MachineLearning"
    ]
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=self.USER_AGENT,
            # No password - read-only M2M authentication
        )
        
        # Verify authentication
        try:
            user = self.reddit.user.me()
            logger.info(f"Authenticated successfully. User: {user}")
        except Exception as e:
            logger.error(f"Authentication check (read-only mode): {e}")
        
        logger.info("Harvester initialized with Responsible Builder Policy compliance")
    
    def fetch_subreddit_posts(
        self, 
        subreddit_name: str, 
        limit: int = 25,
        time_filter: str = 'day'
    ) -> List[TelemetryRecord]:
        """
        Fetch posts from a specific subreddit with rate limit compliance.
        
        Args:
            subreddit_name: Name of the subreddit to monitor
            limit: Maximum posts to fetch (kept low for compliance)
            time_filter: Time window for posts ('hour', 'day', 'week', 'month')
        """
        records = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Use top posts instead of new to reduce polling frequency needs
            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                record = TelemetryRecord(
                    id=submission.id,
                    subreddit=subreddit_name,
                    title=submission.title,
                    author=str(submission.author) if submission.author else '[deleted]',
                    created_utc=submission.created_utc,
                    url=submission.url,
                    selftext=submission.selftext[:1000],  # Truncate for storage
                    score=submission.score,
                    num_comments=submission.num_comments,
                    permalink=f"https://reddit.com{submission.permalink}",
                    harvested_at=datetime.now(timezone.utc).isoformat()
                )
                records.append(record)
            
            logger.info(f"Fetched {len(records)} records from r/{subreddit_name}")
            
        except Exception as e:
            logger.error(f"Error fetching from r/{subreddit_name}: {e}")
        
        return records
    
    def harvest_all(self) -> Dict[str, Any]:
        """
        Execute harvest across all target subreddits.
        
        Returns:
            Dictionary containing harvest metadata and results
        """
        harvest_id = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        all_records = []
        
        logger.info(f"Starting harvest cycle {harvest_id}")
        
        for subreddit in self.TARGET_SUBREDDITS:
            # PRAW automatically handles rate limiting between requests
            records = self.fetch_subreddit_posts(subreddit, limit=25)
            all_records.extend(records)
            
            # Small delay between subreddits for ultra-safe compliance
            time.sleep(2)
        
        result = {
            'harvest_id': harvest_id,
            'harvested_at': datetime.now(timezone.utc).isoformat(),
            'total_records': len(all_records),
            'subreddits_checked': len(self.TARGET_SUBREDDITS),
            'records': [asdict(r) for r in all_records]
        }
        
        logger.info(f"Harvest cycle {harvest_id} complete. Total records: {len(all_records)}")
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], output_dir: str = 'data'):
        """Save harvest results to JSON file."""
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/harvest_{data['harvest_id']}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to {filename}")
        return filename


def main():
    """Main entry point for harvester execution."""
    harvester = RedditTelemetryHarvester()
    
    # Execute harvest
    results = harvester.harvest_all()
    
    # Save results
    output_file = harvester.save_to_json(results)
    
    # Summary output for CI/CD pipelines
    print(f"\n{'='*60}")
    print(f"HARVEST COMPLETE")
    print(f"{'='*60}")
    print(f"Harvest ID: {results['harvest_id']}")
    print(f"Total Records: {results['total_records']}")
    print(f"Subreddits Monitored: {results['subreddits_checked']}")
    print(f"Output File: {output_file}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
