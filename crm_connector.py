#!/usr/bin/env python3
import logging
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime
from time import sleep

logger = logging.getLogger(__name__)

class CRMConnector:
      """HubSpot CRM connector for lead management"""

    def __init__(self, config):
              self.config = config
              self.base_url = config.crm_api_url or 'https://api.hubapi.com'
              self.headers = {'Authorization': f'Bearer {config.crm_api_key}'}
              self.max_retries = 3

    def fetch_leads(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
              """Fetch leads from CRM"""
              try:
                            url = f'{self.base_url}/crm/v3/objects/contacts'
                            params = {'limit': limit or 100}
                            response = requests.get(url, headers=self.headers, params=params)
                            response.raise_for_status()

            data = response.json()
            leads = []
            for item in data.get('results', []):
                              lead = item.get('properties', {})
                              lead['id'] = item.get('id')
                              leads.append(lead)

            logger.info(f'Fetched {len(leads)} leads from CRM')
            return leads
except Exception as e:
            logger.error(f'Error fetching leads: {e}')
            return []

    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
              """Update lead in CRM"""
              try:
                            url = f'{self.base_url}/crm/v3/objects/contacts/{lead_id}'
                            payload = {'properties': data}
                            response = requests.patch(url, json=payload, headers=self.headers)
                            response.raise_for_status()
                            logger.info(f'Updated lead {lead_id}')
                            return True
except Exception as e:
            logger.error(f'Error updating lead {lead_id}: {e}')
            return False

    def log_activity(self, email: str, activity_type: str, details: Dict) -> bool:
              """Log activity for a lead"""
              try:
                            activity = {
                                              'email': email,
                                              'type': activity_type,
                                              'timestamp': datetime.now().isoformat(),
                                              'details': details
                            }
                            logger.info(f'Logged activity: {activity_type} for {email}')
                            return True
except Exception as e:
            logger.error(f'Error logging activity: {e}')
            return False

    def sync_activities(self, activities: List[Dict]) -> Dict[str, int]:
              """Sync multiple activities"""
              stats = {'success': 0, 'failed': 0}
              for activity in activities:
                            if self.log_activity(activity.get('email'), activity.get('type'), activity.get('details')):
                                              stats['success'] += 1
else:
                stats['failed'] += 1
          return stats
