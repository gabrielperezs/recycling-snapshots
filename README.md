# Recycling EBS snapshots in AWS

## Creating automatic snapshots with CloudWatchs Events

[Tutorial to create automatic EBS snapshots](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/TakeScheduledSnapshot.html)

## Description

This software will read all the rules created in CloudWatch. Will discard all rules to keep just the EBS snapshots targers (*Built-in target*).

Following the volume of each target will find the EC2 instance attached to this volume and also the snapshots of this volume. Then will tag the snapshots to make easy identification, ej:

|  Key | Value  | 
|---|---|
| Device | /dev/sdb  |
| Name | Backup: MySQL |
| recyclable | True |

### Deletion

If you use the "--no-dry" the snapshots older than 10 days will be deleted. If you want to change the days use "--days 5" to delete the older than 5 days.

## How to use

```
Recycling and tagging EBS snapshots using the AWS API

optional arguments:
  -h, --help         show this help message and exit
  --profile PROFILE  Profile name for AWS credentials
  --days DAYS        remove snapshots older than X days
  --dry DRY          dry run (by default)
  --no-dry           run in real mode. CHANGES WILL BE APPLY.
  --verbose          Verbose level - Critical: 0, Info: 1, Debug: 2. Default: 1

NOTE: by default will run in DRY mode
```

