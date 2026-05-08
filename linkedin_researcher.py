#!/usr/bin/env python3
import logging
from typing import Dict, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class LinkedInResearcher:
      """Research leads on LinkedIn and gather insights"""

    def __init__(self, config):
              self.config = config
              self.api_headers = {'User-Agent': 'Mozilla/5.0'}
              self.cache = {}

    def research_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
              """Research a lead and return insights"""
              email = lead.get('email', '')
              if email in self.cache:
                            return self.cache[email]

              insights = {
                  'email': email,
                  'profile_url': lead.get('linkedin_url', ''),
                  'company': lead.get('company', ''),
                  'title': lead.get('title', ''),
                  'insights': self._extract_insights(lead),
                  'researched_at': datetime.now().isoformat(),
                  'personalization': self._generate_personalization(lead)
              }

        self.cache[email] = insights
        logger.info(f"Researched lead: {email}")
        return insights

    def _extract_insights(self, lead: Dict[str, Any]) -> Dict[str, str]:
              """Extract key insights from lead data"""
              insights = {}

        if lead.get('company'):
                      insights['company_size'] = self._estimate_company_size(lead.get('company_size', 'unknown'))

        if lead.get('title'):
                      insights['seniority'] = self._assess_seniority(lead.get('title', ''))

        if lead.get('recent_activity'):
                      insights['engagement_level'] = 'active'

        return insights

    def _estimate_company_size(self, size: str) -> str:
              """Estimate company size"""
              if '10000' in str(size) or 'enterprise' in str(size).lower():
                            return 'enterprise'
elif '1000' in str(size):
            return 'large'
elif '100' in str(size):
            return 'medium'
else:
            return 'startup'

    def _assess_seniority(self, title: str) -> str:
              """Assess lead seniority from title"""
              title_lower = title.lower()
              if any(w in title_lower for w in ['ceo', 'founder', 'president', 'director']):
                            return 'executive'
elif any(w in title_lower for w in ['manager', 'lead', 'senior']):
            return 'manager'
else:
            return 'individual contributor'

    def _generate_personalization(self, lead: Dict) -> Dict[str, str]:
              """Generate personalization variables"""
              return {
                  'recent_post': lead.get('recent_post', ''),
                  'shared_connections': lead.get('connections_count', 0),
                  'industry_expertise': lead.get('industry', '')
              }

    def batch_research(self, leads: list) -> list:
              """Research multiple leads"""
              return [self.research_lead(lead) for lead in leads]
      
