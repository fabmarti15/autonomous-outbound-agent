#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Dict, List, Any
from datetime import datetime
import logging

from agent_orchestrator import AgentOrchestrator
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
      parser = argparse.ArgumentParser(
                description='Autonomous Outbound Sales Agent',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog='''
                Examples:
                  python main.py score --input leads.json --output scores.json
                    python main.py outreach --limit 50 --tier hot
                      python main.py sync --full-sync
                        python main.py execute --campaign Q2-2026
                                '''
      )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Score command
    score_parser = subparsers.add_parser('score', help='Score leads by quality and fit')
    score_parser.add_argument('--input', required=True, help='Input JSON file with leads')
    score_parser.add_argument('--output', required=True, help='Output file for scored leads')
    score_parser.add_argument('--threshold', type=float, default=30, help='Minimum score threshold')

    # Outreach command
    outreach_parser = subparsers.add_parser('outreach', help='Generate outreach messages')
    outreach_parser.add_argument('--limit', type=int, default=100, help='Max leads to process')
    outreach_parser.add_argument('--tier', choices=['hot', 'warm', 'cold'], help='Filter by lead tier')
    outreach_parser.add_argument('--personalize', action='store_true', help='Use AI personalization')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync with CRM')
    sync_parser.add_argument('--full-sync', action='store_true', help='Full sync with CRM')
    sync_parser.add_argument('--leads-only', action='store_true', help='Sync leads only')

    # Execute campaign
    execute_parser = subparsers.add_parser('execute', help='Execute full campaign')
    execute_parser.add_argument('--campaign', required=True, help='Campaign ID')
    execute_parser.add_argument('--dry-run', action='store_true', help='Preview without sending')
    execute_parser.add_argument('--workers', type=int, default=3, help='Parallel workers')

    args = parser.parse_args()

    if not args.command:
              parser.print_help()
              return 1

    try:
              config = Config()
              orchestrator = AgentOrchestrator(config)

        if args.command == 'score':
                      logger.info(f'Scoring leads from {args.input}')
                      results = orchestrator.score_leads_batch(args.input, args.threshold)
                      with open(args.output, 'w') as f:
                                        json.dump(results, f, indent=2, default=str)
                                    logger.info(f'Scored {len(results)} leads, saved to {args.output}')

elif args.command == 'outreach':
            logger.info(f'Generating outreach for {args.limit} leads')
            messages = orchestrator.generate_outreach(
                              limit=args.limit,
                              tier=args.tier,
                              personalize=args.personalize
            )
            logger.info(f'Generated {len(messages)} messages')
            for msg in messages[:5]:
                              print(f"\nTo: {msg['to']}\nMessage: {msg['subject']}\n{msg['body'][:100]}...")

elif args.command == 'sync':
            logger.info('Syncing with CRM')
            sync_result = orchestrator.sync_crm(full_sync=args.full_sync)
            logger.info(f'Sync complete: {sync_result}')

elif args.command == 'execute':
            logger.info(f'Executing campaign: {args.campaign}')
            if args.dry_run:
                              logger.info('DRY RUN MODE - No messages will be sent')
                          campaign_result = orchestrator.execute_campaign(
                                            campaign_id=args.campaign,
                                            dry_run=args.dry_run,
                                            workers=args.workers
)
            logger.info(f'Campaign result: {campaign_result}')

except Exception as e:
        logger.error(f'Error: {str(e)}', exc_info=True)
        return 1

    return 0

if __name__ == '__main__':
      sys.exit(main())
