#!/usr/bin/env python3
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import openai
from jinja2 import Template

logger = logging.getLogger(__name__)

class MessageGenerator:
      """Generates personalized outreach messages using OpenAI"""

    MESSAGE_TEMPLATES = {
              'hot': '''
              Subject: Quick opportunity for {{company}}

              Hi {{first_name}},

              I noticed {{company}} is doing great work in {{industry}}. Your background in {{title}} makes me think you might be interested in {{value_prop}}.

              Would you have 15 minutes for a quick chat?

              Best,
              {{sender_name}}
                      ''',
              'warm': '''
              Subject: {{company}} - quick thought

              Hi {{first_name}},

              I came across your profile and {{company}}'s work. Thought it might be worth a conversation.

              Free next week?

              {{sender_name}}
                      ''',
              'cold': '''
              Subject: Quick intro

              Hi {{first_name}},

              Thought you might find this interesting given your role at {{company}}.

              Let me know if worth chatting.

              {{sender_name}}
                      '''
    }

    def __init__(self, config):
              self.config = config
              openai.api_key = config.openai_api_key
              self.model = config.openai_model or 'gpt-4'

    def generate_message(self, lead: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, str]:
              """Generate personalized message for a lead"""
              context = context or {}

        # Prepare template variables
              variables = {
                  'company': lead.get('company', 'your company'),
                  'first_name': lead.get('first_name', 'there'),
                  'title': lead.get('title', 'your role'),
                  'industry': lead.get('industry', 'your industry'),
                  'value_prop': self.config.value_proposition,
                  'sender_name': self.config.sender_name,
              }
              variables.update(context.get('personalization', {}))

        # Determine message tier
              score = context.get('score', 50)
              if score >= 70:
                            tier = 'hot'
elif score >= 40:
            tier = 'warm'
else:
            tier = 'cold'

        # Generate base message from template
          template_text = self.MESSAGE_TEMPLATES.get(tier, self.MESSAGE_TEMPLATES['warm'])
        template = Template(template_text)
        base_message = template.render(**variables)

        # Enhance with AI if personalization enabled
        if self.config.ai_personalization_enabled and context.get('insights'):
                      base_message = self._enhance_with_ai(base_message, lead, context['insights'])

        # Parse subject and body
        lines = base_message.strip().split('\n')
        subject = next((line.replace('Subject: ', '') for line in lines if line.startswith('Subject:')), '')
        body = '\n'.join(line for line in lines if not line.startswith('Subject:') and line.strip()).strip()

        return {
                      'to': lead.get('email', ''),
                      'subject': subject,
                      'body': body,
                      'tier': tier,
                      'lead_id': lead.get('id', ''),
                      'generated_at': datetime.now().isoformat(),
                      'personalized': bool(context.get('insights'))
        }

    def _enhance_with_ai(self, base_message: str, lead: Dict, insights: Dict) -> str:
              """Enhance message with AI personalization"""
              try:
                            prompt = f'''
                            You are an expert sales copywriter. Personalize this message based on the lead's profile:

                            Base message:
                            {base_message}

                            Lead insights:
                            {json.dumps(insights, indent=2)}

                            Rules:
                            - Keep it concise (max 100 words body)
                            - Sound natural and friendly
                            - Reference specific insights from the lead's profile
                            - Include a clear call-to-action

                            Respond with only the enhanced message, no explanations.
                                        '''

            response = openai.ChatCompletion.create(
                              model=self.model,
                              messages=[{"role": "user", "content": prompt}],
                              temperature=0.7,
                              max_tokens=300
            )

            enhanced = response.choices[0].message.content.strip()
            logger.info(f"AI-enhanced message for {lead.get('email')}")
            return enhanced

except Exception as e:
            logger.warning(f"AI enhancement failed: {e}. Using base message.")
            return base_message

    def generate_batch(self, leads: list, context_list: Optional[list] = None) -> list:
              """Generate messages for multiple leads"""
              context_list = context_list or [{}] * len(leads)
              messages = []

        for lead, context in zip(leads, context_list):
                      try:
                                        msg = self.generate_message(lead, context)
                                        messages.append(msg)
except Exception as e:
                logger.error(f"Failed to generate message for {lead.get('email')}: {e}")

        return messages
