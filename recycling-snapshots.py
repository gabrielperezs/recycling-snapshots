#!/usr/bin/python2.7

import sys
import boto3
import logging
import argparse
import datetime
import rsevents
import rsebs


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('ebs-lifecycle')

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Recycling and tagging EBS snapshots using the AWS API",
        epilog="NOTE: by default will run in DRY mode"
    )
    parser.add_argument('--profile', type=str, required=False, default="",
                        help='Profile name for AWS credentials')
    parser.add_argument('--days', type=int, required=True, default=10,
                        help='remove snapshots older than X days')
    parser.add_argument('--dry', type=bool, default=True,
                        help='dry run (by default)')
    parser.add_argument('--no-dry', dest='dry', action='store_false',
                        help='run in real mode. CHANGES WILL BE APPLY.')

    args = parser.parse_args()
    
    if args.profile == "":
        boto3.setup_default_session()
    else:
        boto3.setup_default_session(profile_name=args.profile)

    rsevents.set_client()
    rsebs.set_client()

    if args.dry is False:
        rsebs.unset_drymode()
        logger.warning("Runinng in real mode")
    else:
        rsebs.set_drymode()
        logger.info("Runinng in DRY mode (no changes will be apply)")
        

    today = datetime.datetime.utcnow()

    rules = rsevents.get_rules()
    if not rules:
        sys.exit()

    for rule in rules:

        targets = rsevents.get_targets(rule["Name"])

        if not targets:
            logger.warning("No targets found in rule %s", rule["Name"])
            continue

        logger.debug("In %s we found %s targets", rule["Name"], len(targets))

        for target in targets:
            logger.debug("Target found %s", target["VolumeID"])
            snapshots = rsebs.get_snapshots(target["VolumeID"])

            if not snapshots:
                logger.warning("No snapshots found for the Volume %s in rule %s", target["VolumeID"], rule["Name"])
                continue

            logger.info("In rule %s volume %s found %s snapshots", rule["Name"], target["VolumeID"], len(snapshots))

            for snapshot in snapshots:
                rsebs.tag_snapshot(snapshot, rule["Name"])
                diff = abs(today.date() - snapshot["StartTime"].date()).days
                if diff >= args.days:
                    
                    if args.dry is False:
                        logger.warning("Snapshot %s date %s deleted", snapshot["SnapshotId"], snapshot["StartTime"])
                        snapshot["oSnapshot"].delete(DryRun=False)
                    else:
                        logger.warning("Snapshot %s date %s will be delete", snapshot["SnapshotId"], snapshot["StartTime"])



