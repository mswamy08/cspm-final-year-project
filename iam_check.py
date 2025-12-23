def list_admin_users(session):
    iam = session.client('iam')
    paginator = iam.get_paginator('list_users')
    admin_users = []
    for page in paginator.paginate():
        for user in page.get('Users', []):
            username = user['UserName']
            try:
                policies = iam.list_attached_user_policies(UserName=username).get('AttachedPolicies', [])
                for policy in policies:
                    if policy.get('PolicyName') == 'AdministratorAccess' or 'AdministratorAccess' in policy.get('PolicyName', ''):
                        admin_users.append(username)
                        break
            except Exception:
                continue
    return admin_users
