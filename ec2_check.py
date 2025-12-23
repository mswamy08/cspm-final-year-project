def check_public_ec2(session):
    ec2 = session.client('ec2')
    public_instances = []
    try:
        paginator = ec2.get_paginator('describe_instances')
        for page in paginator.paginate():
            for reservation in page.get('Reservations', []):
                for inst in reservation.get('Instances', []):
                    if inst.get('PublicIpAddress'):
                        public_instances.append({
                            'InstanceId': inst.get('InstanceId'),
                            'PublicIp': inst.get('PublicIpAddress')
                        })
    except Exception:
        pass
    return public_instances
