import boto3
import logging

logger = logging.getLogger(__package__)

dry = True
client = None
ec2 = None

def set_drymode():
    global dry
    dry = True

def unset_drymode():
    global dry
    dry = False
    

def set_client():
    """Define global variables to use the same API connection"""
    global client, ec2
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')

def get_snapshots(volume_id=False):
    """Get list of snapshots filter by the volume_id"""
    response = client.describe_snapshots(
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [volume_id,]
            },
            {
                'Name': 'status',
                'Values': ['completed',]
            }
        ],
    )

    if "Snapshots" not in response or len(response["Snapshots"]) == 0:
        logger.warning("Don't found snapshots of the volume %s", volume_id)
        return False

    snapshots = []

    for _, snapshot in enumerate(response["Snapshots"]):
        # Ignore snapshots created by AMI
        if snapshot["Description"] != "":
            continue

        snapshot["oSnapshot"] = ec2.Snapshot(snapshot["SnapshotId"])

        snapshots.append(snapshot)


    return snapshots


def tag_snapshot(snapshot, name):
    """ Define tag to automatic snapshots """

    has_tag_name = False
    has_tag_device = False

    if "Tags" in snapshot and len(snapshot["Tags"]) > 0:
        for tag in snapshot["Tags"]:
            if tag["Key"] == "Name" and tag["Value"] != "":
                has_tag_name = True
            elif tag["Key"] == "Device" and tag["Value"] != "":
                has_tag_device = True

    if has_tag_name and has_tag_device:
        return True

    if "oSnapshot" not in snapshot:
        snapshot["oSnapshot"] = ec2.Snapshot(snapshot["SnapshotId"])

    if "oVolume" not in snapshot:
        snapshot["oVolume"] = ec2.Volume(snapshot["VolumeId"])

    _tags = [
        {
            'Key': 'Name',
            'Value': "Backup: {}".format(name),
        },
        {
            'Key': "Device",
            'Value': "{}".format(snapshot["oVolume"].attachments[0]["Device"]),
        },
        {
            'Key': 'recyclable',
            'Value': "True",
        },
    ]

    if dry is False:
        tag = snapshot["oSnapshot"].create_tags(DryRun=False, Tags=_tags)

    logger.info("The snapshot %s were tagged %s = %s [%s]",
                snapshot["SnapshotId"],
                "Name",
                "Backup: {}".format(_tags),
                dry)
    