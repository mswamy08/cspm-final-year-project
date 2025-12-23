import boto3

def check_security_groups(session):
    client = session.client('ec2')
    response = client.describe_security_groups()
    
    findings = []
    for sg in response['SecurityGroups']:
        for perm in sg.get('IpPermissions', []):
            for ip_range in perm.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    findings.append({
                        "GroupId": sg['GroupId'],
                        "Port": perm.get('FromPort'),
                        "Protocol": perm.get('IpProtocol'),
                        "Description": sg.get('Description', 'No description')
                    })
    return findings
