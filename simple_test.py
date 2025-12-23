#!/usr/bin/env python3
"""
Simple Testing Guide for CSPM Tool
Test components that work with current AWS permissions
"""
from dotenv import load_dotenv
import boto3
import sys
import os

# Load environment variables
load_dotenv()

def test_basic_aws():
    """Test basic AWS connectivity (this works)"""
    print("🔍 Testing AWS Connection...")
    try:
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ User: {identity['Arn'].split('/')[-1]}")
        return session
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

def test_environment_variables():
    """Test .env file loading"""
    print("\n🔧 Testing Environment Variables...")
    
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: Not found")

def test_flask_app():
    """Test if Flask app can start"""
    print("\n🌐 Testing Flask App...")
    try:
        # Just import to check if all dependencies exist
        import flask
        print("✅ Flask available")
        
        # Check if app.py can be imported
        if os.path.exists('app.py'):
            print("✅ app.py exists")
        else:
            print("❌ app.py not found")
            
        return True
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

def test_cli_tool():
    """Test CLI tool"""
    print("\n🖥️ Testing CLI Tool...")
    try:
        if os.path.exists('cli.py'):
            print("✅ cli.py exists")
            # Try to import (without running)
            spec = __import__('cli')
            print("✅ CLI module can be imported")
        else:
            print("❌ cli.py not found")
    except Exception as e:
        print(f"❌ CLI import failed: {e}")

def test_ec2_specifically():
    """Test EC2 module which seemed to work"""
    print("\n🖥️ Testing EC2 Module (Working)...")
    try:
        session = boto3.Session()
        ec2 = session.client('ec2', region_name='us-east-1')
        
        # Try to describe instances (this might work)
        try:
            response = ec2.describe_instances()
            instance_count = sum(len(reservation['Instances']) for reservation in response['Reservations'])
            print(f"✅ Found {instance_count} EC2 instances")
            
            # Check for public instances
            public_instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if instance.get('PublicIpAddress'):
                        public_instances.append({
                            'InstanceId': instance['InstanceId'],
                            'PublicIp': instance['PublicIpAddress'],
                            'State': instance['State']['Name']
                        })
            
            print(f"✅ Found {len(public_instances)} public instances")
            for inst in public_instances:
                print(f"   - {inst['InstanceId']}: {inst['PublicIp']} ({inst['State']})")
                
        except Exception as e:
            print(f"❌ EC2 describe failed: {e}")
            
    except Exception as e:
        print(f"❌ EC2 setup failed: {e}")

def simple_permission_test():
    """Test what AWS permissions we actually have"""
    print("\n🔐 Testing AWS Permissions...")
    session = boto3.Session()
    
    # Test different services
    services_to_test = [
        ('STS', 'sts', 'get_caller_identity'),
        ('EC2 Instances', 'ec2', 'describe_instances'),
        ('EC2 Security Groups', 'ec2', 'describe_security_groups'),
        ('S3 Buckets', 's3', 'list_buckets'),
        ('IAM Users', 'iam', 'list_users'),
        ('CloudTrail', 'cloudtrail', 'describe_trails')
    ]
    
    working_services = []
    
    for service_name, service_code, operation in services_to_test:
        try:
            client = session.client(service_code, region_name='us-east-1')
            method = getattr(client, operation)
            
            if operation == 'get_caller_identity':
                method()
            elif operation == 'describe_instances':
                method()
            elif operation == 'describe_security_groups':
                method()
            elif operation == 'list_buckets':
                method()
            elif operation == 'list_users':
                method()
            elif operation == 'describe_trails':
                method()
                
            print(f"✅ {service_name}: Permission granted")
            working_services.append(service_name)
            
        except Exception as e:
            print(f"❌ {service_name}: {str(e)[:100]}...")
    
    return working_services

def main():
    print("🛡️ CSPM Tool - Simple Testing")
    print("=" * 60)
    
    # Test basic functionality
    session = test_basic_aws()
    if not session:
        return
    
    test_environment_variables()
    test_flask_app()
    test_cli_tool()
    
    # Test what permissions we have
    working_services = simple_permission_test()
    
    # Test EC2 specifically since it worked
    test_ec2_specifically()
    
    print("\n" + "=" * 60)
    print("📋 QUICK TESTING RECOMMENDATIONS:")
    print("=" * 60)
    
    print("\n🟢 WHAT YOU CAN TEST NOW:")
    for service in working_services:
        print(f"   ✅ {service}")
    
    print(f"\n🔧 TO TEST THE FLASK APP:")
    print(f"   python app.py")
    print(f"   Then visit: http://localhost:5000")
    
    print(f"\n🖥️ TO TEST CLI TOOL:")
    print(f"   python cli.py")
    
    print(f"\n📝 TO TEST INDIVIDUAL MODULES:")
    print(f"   python -c \"from modules.ec2_check import check_public_ec2; import boto3; print(check_public_ec2(boto3.Session()))\"")
    
    print("\n⚠️ AWS PERMISSIONS NEEDED:")
    print("   Your AWS user needs more permissions for full CSPM functionality")
    print("   Contact your AWS admin to add policies for S3, IAM, CloudTrail, etc.")

if __name__ == "__main__":
    main()