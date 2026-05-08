#!/usr/bin/env python3
import json
import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

from linkedin_researcher import LinkedInResearcher
from message_generator import MessageGenerator
from crm_connector import CRMConnector
from lead_scorer import LeadScorer

logger = logging.getLogger(__name__)

class AgentOrchestrator:
      """Main orchestrator for autonomous outbound sales agent"""

    def __init__(self, config):
              self.config = config
              self.researcher = LinkedInResearcher(config)
              self.message_gen = MessageGenerator(config)
              self.crm = CRMConnector(config)
              self.scorer = LeadScorer(config)
              self.activity_log = []

    def score_leads_batch(self, input_file: str, threshold: float = 30) -> List[Dict]:
              """Score leads from input file"""
              with open(input_file, 'r') as f:
                            leads = json.load(f)

              scored_leads = []
              for lead in leads:
                            score_result = self.scorer.score_lead(lead)
                            score_result['threshold_pass'] = score_result['score'] >= threshold
                            scored_leads.append(score_result)
                            logger.info(f"Scored {lead.get('name', 'Unknown')}: {score_result['score']:.1f}")

              return sorted(scored_leads, key=lambda x: x['score'], reverse=True)

    def generate_outreach(self, limit: int = 100, tier: Optional[str] = None, 
                                                   personalize: bool = True) -> List[Dict]:
                                                             """Generate personalized outreach messages"""
                                                             leads = self.crm.fetch_leads(limit=limit * 2)

        # Score and filter
        scored = [self.scorer.score_lead(lead) for lead in leads]

        if tier:
                      tier_map = {'hot': (70, 100), 'warm': (40, 70), 'cold': (0, 40)}
                      min_score, max_score = tier_map.get(tier, (0, 100))
                      scored = [s for s in scored if min_score <= s['score'] <= max_score]

        messages = []
        for lead_data in scored[:limit]:
                      lead = lead_data['lead']

            if personalize:
                              research = self.researcher.research_lead(lead)
                              context = research.get('insights', {})
else:
                  context = {}

            message = self.message_gen.generate_message(lead, context)
            message['score'] = lead_data['score']
            message['tier'] = lead_data['tier']
            messages.append(message)

            logger.info(f"Generated message for {lead.get('email', 'unknown')}")

        return messages

    def sync_crm(self, full_sync: bool = False) -> Dict[str, Any]:
              """Sync with CRM system"""
              logger.info(f'Starting CRM sync (full={full_sync})')

        sync_stats = {
                      'leads_fetched': 0,
                      'leads_updated': 0,
                      'activities_logged': 0,
                      'errors': 0,
                      'timestamp': datetime.now().isoformat()
        }

        try:
                      # Fetch leads
                      leads = self.crm.fetch_leads(limit=None if full_sync else 500)
                      sync_stats['leads_fetched'] = len(leads)

            # Score and update each lead
                      for lead in leads:
                                        try:
                                                              score_data = self.scorer.score_lead(lead)
                                                              self.crm.update_lead(lead['id'], {
                                                                  'score': score_data['score'],
                                                                  'tier': score_data['tier'],
                                                                  'last_scored': datetime.now().isoformat()
                                                              })
                                                              sync_stats['leads_updated'] += 1
        except Exception as e:
                    logger.error(f"Error updating lead {lead.get('id')}: {e}")
                    sync_stats['errors'] += 1

            logger.info(f"Sync complete: {sync_stats}")

except Exception as e:
            logger.error(f"Sync failed: {e}")
            sync_stats['errors'] += 1

        return sync_stats

    def execute_campaign(self, campaign_id: str, dry_run: bool = False, 
                                                 workers: int = 3) -> Dict[str, Any]:
                                                           """Execute full outbound campaign"""
                                                           logger.info(f"Executing campaign {campaign_id} (dry_run={dry_run}, workers={workers})")

        campaign_result = {
                      'campaign_id': campaign_id,
                      'messages_sent': 0,
                      'messages_failed': 0,
                      'leads_researched': 0,
                      'dry_run': dry_run,
                      'start_time': datetime.now().isoformat()
        }

        # Generate messages
        messages = self.generate_outreach(limit=200, personalize=True)

        if dry_run:
                      logger.info(f"DRY RUN: Would send {len(messages)} messages")
                      campaign_result['messages_sent'] = len(messages)
                      return campaign_result

        # Execute with thread pool
        with ThreadPoolExecutor(max_workers=workers) as executor:
                      futures = {}
                      for msg in messages:
                                        future = executor.submit(self._send_message_safe, msg)
                                        futures[future] = msg

                      for future in as_completed(futures):
                                        try:
                                                              if future.result():
                                                                                        campaign_result['messages_sent'] += 1
                                        else:
                                                                  campaign_result['messages_failed'] += 1
                                        except Exception as e:
                                            logger.error(f"Message send failed: {e}")
                                            campaign_result['messages_failed'] += 1

                  campaign_result['end_time'] = datetime.now().isoformat()
        logger.info(f"Campaign result: {campaign_result}")
        return campaign_result

    def _send_message_safe(self, message: Dict) -> bool:
              """Safely send a message with error handling"""
              try:
                            # Simulate message sending (would integrate with email/API)
                            time.sleep(0.1)  # Rate limiting
            logger.info(f"Sent message to {message.get('to')}")
            self.crm.log_activity(message.get('to'), 'message_sent', {'subject': message.get('subject')})
            return True
except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
