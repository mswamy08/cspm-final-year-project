from flask import Flask, render_template, jsonify, request
import boto3
import json
import os
from datetime import datetime
import threading
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import CSPM modules
from modules.s3_check import check_public_buckets
from modules.iam_check import list_admin_users
from modules.ec2_check import check_public_ec2
from modules.cloudtrail_check import check_cloudtrail_enabled
from modules.sg_check import check_security_groups

app = Flask(__name__)

# Global variable to store scan results
scan_results = {
    'last_scan': None,
    's3_findings': [],
    'iam_findings': [],
    'ec2_findings': [],
    'cloudtrail_findings': [],
    'sg_findings': [],
    'scan_status': 'idle',
    'total_issues': 0
}

def perform_aws_scan():
    """Perform AWS security scan and update global results"""
    global scan_results
    
    try:
        scan_results['scan_status'] = 'scanning'
        scan_results['last_scan'] = datetime.now().isoformat()
        
        # Initialize AWS session
        session = boto3.Session()
        
        print("Starting AWS security scan...")
        
        # S3 Check
        print("Scanning S3 buckets...")
        s3_findings = check_public_buckets(session)
        scan_results['s3_findings'] = [{'bucket': bucket, 'risk': 'High', 'type': 'Public Access'} for bucket in s3_findings]
        
        # IAM Check
        print("Scanning IAM users...")
        iam_findings = list_admin_users(session)
        scan_results['iam_findings'] = [{'user': user, 'risk': 'Medium', 'type': 'Admin Access'} for user in iam_findings]
        
        # EC2 Check
        print("Scanning EC2 instances...")
        ec2_findings = check_public_ec2(session)
        scan_results['ec2_findings'] = [{'instance': f"{ec2['InstanceId']}", 'ip': ec2['PublicIp'], 'risk': 'High', 'type': 'Public Instance'} for ec2 in ec2_findings]
        
        # CloudTrail Check
        print("Checking CloudTrail...")
        ct_findings = check_cloudtrail_enabled(session)
        scan_results['cloudtrail_findings'] = [{'issue': issue, 'risk': 'Medium', 'type': 'Logging Issue'} for issue in ct_findings]
        
        # Security Groups Check
        print("Scanning Security Groups...")
        sg_findings = check_security_groups(session)
        scan_results['sg_findings'] = [{'group': sg['GroupId'], 'port': sg['Port'], 'protocol': sg['Protocol'], 'risk': 'High', 'type': 'Open Access'} for sg in sg_findings]
        
        # Calculate total issues
        scan_results['total_issues'] = (
            len(scan_results['s3_findings']) +
            len(scan_results['iam_findings']) +
            len(scan_results['ec2_findings']) +
            len(scan_results['cloudtrail_findings']) +
            len(scan_results['sg_findings'])
        )
        
        scan_results['scan_status'] = 'completed'
        print(f"Scan completed. Total issues found: {scan_results['total_issues']}")
        
    except Exception as e:
        scan_results['scan_status'] = 'error'
        scan_results['error'] = str(e)
        print(f"Scan failed: {e}")

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """Start a new AWS security scan"""
    if scan_results['scan_status'] == 'scanning':
        return jsonify({'status': 'already_scanning'})
    
    # Start scan in background thread
    scan_thread = threading.Thread(target=perform_aws_scan)
    scan_thread.daemon = True
    scan_thread.start()
    
    return jsonify({'status': 'scan_started'})

@app.route('/api/scan/status')
def scan_status():
    """Get current scan status and results"""
    return jsonify(scan_results)

@app.route('/api/findings')
def get_findings():
    """Get all security findings"""
    return jsonify({
        'summary': {
            's3_issues': len(scan_results['s3_findings']),
            'iam_issues': len(scan_results['iam_findings']),
            'ec2_issues': len(scan_results['ec2_findings']),
            'cloudtrail_issues': len(scan_results['cloudtrail_findings']),
            'sg_issues': len(scan_results['sg_findings']),
            'total_issues': scan_results['total_issues'],
            'last_scan': scan_results['last_scan'],
            'status': scan_results['scan_status']
        },
        'findings': {
            's3': scan_results['s3_findings'],
            'iam': scan_results['iam_findings'],
            'ec2': scan_results['ec2_findings'],
            'cloudtrail': scan_results['cloudtrail_findings'],
            'security_groups': scan_results['sg_findings']
        }
    })

@app.route('/api/aws/test')
def test_aws_connection():
    """Test AWS credentials and connection"""
    try:
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        return jsonify({
            'status': 'connected',
            'account_id': identity.get('Account'),
            'user_arn': identity.get('Arn'),
            'user_id': identity.get('UserId')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting AWS CSPM Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:5000")
    print("🔑 Make sure your AWS credentials are configured!")
    print("   - Use 'aws configure' or set environment variables")
    print("   - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION")
    
    app.run(debug=True, port=5000)