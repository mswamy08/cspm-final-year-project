# 🧪 **CSPM Tool Testing Guide**

## **Current Status Summary:**
- ✅ **Flask App**: Ready to run and test
- ✅ **Environment Variables**: Working perfectly  
- ✅ **AWS Connection**: Connected to account 483338549572
- ⚠️ **AWS Permissions**: Limited (only STS access currently)
- ✅ **Dependencies**: All installed

---

## **🚀 Method 1: Test Flask Web Dashboard**

### Start the web application:
```bash
python app.py
```

### Test the web interface:
1. **Dashboard**: http://localhost:5000
2. **AWS Test API**: http://localhost:5000/api/aws/test  
3. **Security Findings**: http://localhost:5000/api/findings

### What you'll see:
- Web dashboard with AWS account info
- Interactive buttons for each security check
- Real-time results (limited by current permissions)

---

## **🖥️ Method 2: Test CLI Tool**

### Run command-line scanning:
```bash
python cli.py
```

### Expected behavior:
- Shows AWS account information
- Attempts security scans across all services
- Generates CSV reports in `/logs` folder
- Shows permission errors for restricted services

---

## **🔍 Method 3: Test Individual Components**

### Test Environment Loading:
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Region:', os.getenv('AWS_DEFAULT_REGION'))"
```

### Test AWS Connection:
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import boto3; print('Account:', boto3.client('sts').get_caller_identity()['Account'])"
```

### Test Report Generation:
```bash
python -c "from modules.report import export_csv; export_csv([{'Item': 'Test', 'Risk': 'High'}], 'test.csv'); print('Report created')"
```

---

## **🛠️ Method 4: Debug Mode Testing**

### Start Flask in debug mode:
```bash
python -c "from app import app; app.run(debug=True, port=5001)"
```

### Benefits of debug mode:
- Shows detailed error messages
- Auto-reloads when files change
- Better for development testing

---

## **📊 Method 5: Test with Mock Data**

### Create test data and generate reports:
```bash
python -c "
from modules.report import export_csv
test_findings = [
    {'Item': 'test-bucket', 'Risk': 'High', 'Type': 'Public S3 Bucket'},
    {'Item': 'test-instance', 'Risk': 'Medium', 'Type': 'Public EC2'},
    {'Item': 'admin-user', 'Risk': 'Critical', 'Type': 'Admin Access'}
]
export_csv(test_findings, 'logs/mock_findings.csv')
print('Mock report generated in logs/mock_findings.csv')
"
```

---

## **⚡ Quick Testing Commands**

### Test all at once:
```bash
# Test environment
python simple_test.py

# Test web app (in separate terminal)
python app.py

# Test CLI tool 
python cli.py
```

---

## **🔧 Current Limitations & Solutions**

### **Permission Issues:**
Your AWS user has limited permissions. Here's what works vs. what doesn't:

**✅ WORKING:**
- AWS account identification
- Environment variable loading
- Flask web interface
- Report generation

**❌ NOT WORKING (needs more AWS permissions):**
- S3 bucket scanning
- IAM user analysis  
- EC2 instance checking
- CloudTrail auditing
- Security group analysis

### **To get full functionality:**
1. **Ask your AWS administrator** to attach these policies to your `cspm-user`:
   - `AmazonS3ReadOnlyAccess`
   - `IAMReadOnlyAccess` 
   - `AmazonEC2ReadOnlyAccess`
   - `CloudTrailReadOnlyAccess`

2. **Or create a custom policy** with these permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:ListAllMyBuckets",
                   "s3:GetBucketAcl",
                   "iam:ListUsers",
                   "iam:GetUserPolicy",
                   "ec2:DescribeInstances",
                   "ec2:DescribeSecurityGroups",
                   "cloudtrail:DescribeTrails"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

---

## **📝 Testing Checklist**

- [ ] Environment variables load correctly
- [ ] AWS connection established  
- [ ] Flask app starts without errors
- [ ] Web dashboard loads at localhost:5000
- [ ] CLI tool runs and shows account info
- [ ] Reports generate in logs folder
- [ ] All Python dependencies installed

---

## **🎯 Next Steps for Full Testing**

1. **Get AWS permissions** from your administrator
2. **Test with real AWS resources** (S3 buckets, EC2 instances, etc.)
3. **Set up automation** with scheduled scans
4. **Configure alerts** for security findings

---

**💡 Pro Tip:** Even with limited permissions, you can test the tool's structure, web interface, and report generation capabilities!