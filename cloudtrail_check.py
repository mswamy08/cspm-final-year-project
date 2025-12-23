import boto3

def check_cloudtrail_enabled(session):
    client = session.client('cloudtrail')
    trails = client.describe_trails()['trailList']
    
    findings = []
    if not trails:
        findings.append("No CloudTrails configured!")
    else:
        for trail in trails:
            status = client.get_trail_status(Name=trail['Name'])
            if not status['IsLogging']:
                findings.append(f"CloudTrail '{trail['Name']}' is NOT logging")
    
    return findings
