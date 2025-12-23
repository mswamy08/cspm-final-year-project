def list_s3_buckets(session):
    s3 = session.client('s3')
    response = s3.list_buckets()
    return [bucket['Name'] for bucket in response.get('Buckets', [])]

def check_public_buckets(session):
    s3 = session.client('s3')
    public_buckets = []
    for bucket in list_s3_buckets(session):
        try:
            acl = s3.get_bucket_acl(Bucket=bucket)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if grantee.get('Type') == 'Group' and 'AllUsers' in grantee.get('URI', ''):
                    public_buckets.append(bucket)
        except Exception as e:
            # skip buckets we can't access
            continue
    return public_buckets
