import boto3
import logging

logger = logging.getLogger(__package__)

client = None

def set_client():
    global client
    client = boto3.client('events')
    

def get_rules():
    rules = client.list_rules()
    if "Rules" not in rules:
        logger.critical("Imposible to read the rules")
        return False

    if len(rules["Rules"]) == 0:
        logger.error("Don't exists rules in this account")
        return False


    return rules["Rules"]


def get_targets(rule=False):
    
    response = client.list_targets_by_rule(
        Rule=rule,
        Limit=20,
    )

    if "Targets" not in response or response["Targets"] == 0:
        logger.warning("The rule %s don't has targets", rule)
        return False

    for tID, target in enumerate(response["Targets"]):
        
        # We keep just EBS snapshots targets
        if "EBSCreateSnapshot" not in response["Targets"][tID]["Arn"]:
            del response["Targets"][tID]
            continue

        # Save the volume ID
        volume = target["Input"].split("/")
        if volume[0][-6:] == "volume":
            response["Targets"][tID]["VolumeID"] = volume[1][:-1]

    return response["Targets"]