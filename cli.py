import boto3
import os
import subprocess
import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import CSPM modules
from modules.s3_check import check_public_buckets
from modules.iam_check import list_admin_users
from modules.ec2_check import check_public_ec2
from modules.cloudtrail_check import check_cloudtrail_enabled
from modules.sg_check import check_security_groups
from modules.report import export_csv

# --- ALERT FUNCTIONS ---
def send_email_alert(subject, body, to_email):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = "youremail@gmail.com"  # Replace with your email
        msg['To'] = to_email

        # Gmail SMTP (App Password required)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("youremail@gmail.com", "your-app-password")  # Replace with App Password
        server.send_message(msg)
        server.quit()
        print(f"[INFO] Email alert sent to {to_email}")
    except Exception as e:
        print(f"[WARN] Failed to send email: {e}")

def send_slack_alert(message, webhook_url):
    if not webhook_url or webhook_url.startswith("https://hooks.slack.com/services/XXXXXXXXX"):
        print("[WARN] Slack webhook not set or invalid. Skipping Slack alert.")
        return
    try:
        response = requests.post(webhook_url, json={"text": message})
        if response.status_code == 200:
            print("[INFO] Slack alert sent successfully")
        else:
            print(f"[WARN] Slack alert failed: {response.text}")
    except Exception as e:
        print(f"[WARN] Error sending Slack alert: {e}")

# --- HELPER TO OPEN CSV ---
def open_csv_in_excel(file_path):
    if os.name == 'nt':
        try:
            subprocess.Popen(['start', '', file_path], shell=True)
        except Exception as e:
            print(f"[WARN] Could not open {file_path} in Excel: {e}")

# --- MAIN FUNCTION ---
def main():
    session = boto3.Session()
    os.makedirs("logs", exist_ok=True)

    # Slack webhook (replace with your valid webhook URL)
    slack_webhook = "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXX"

    # --- S3 ---
    print("\n--- Public S3 Buckets ---")
    s3_findings = check_public_buckets(session)
    if not s3_findings:
        print("No findings.")
    else:
        for f in s3_findings:
            print(f)
        alert_msg = "CSPM ALERT: Public S3 Buckets:\n" + "\n".join(s3_findings)
        send_email_alert("CSPM Alert: Public S3 Buckets", alert_msg, "admin@example.com")
        send_slack_alert(alert_msg, slack_webhook)
    s3_file = "logs/public_s3_buckets.csv"
    export_csv([{"Bucket": b} for b in s3_findings], s3_file)
    open_csv_in_excel(s3_file)

    # --- IAM ---
    print("\n--- IAM Admin Users ---")
    iam_findings = list_admin_users(session)
    if not iam_findings:
        print("No findings.")
    else:
        for f in iam_findings:
            print(f)
        alert_msg = "CSPM ALERT: IAM Admin Users:\n" + "\n".join(iam_findings)
        send_email_alert("CSPM Alert: IAM Admin Users", alert_msg, "admin@example.com")
        send_slack_alert(alert_msg, slack_webhook)
    iam_file = "logs/iam_admin_users.csv"
    export_csv([{"AdminUser": u} for u in iam_findings], iam_file)
    open_csv_in_excel(iam_file)

    # --- EC2 ---
    print("\n--- Public EC2 Instances ---")
    ec2_findings = check_public_ec2(session)
    if not ec2_findings:
        print("No findings.")
    else:
        for f in ec2_findings:
            print(f)
        alert_msg = "CSPM ALERT: Public EC2 Instances:\n" + "\n".join([f"{i['InstanceId']} - {i['PublicIp']}" for i in ec2_findings])
        send_email_alert("CSPM Alert: Public EC2 Instances", alert_msg, "admin@example.com")
        send_slack_alert(alert_msg, slack_webhook)
    ec2_file = "logs/public_ec2_instances.csv"
    export_csv(ec2_findings, ec2_file)
    open_csv_in_excel(ec2_file)

    # --- CloudTrail ---
    print("\n--- CloudTrail Logging ---")
    cloudtrail_findings = check_cloudtrail_enabled(session)
    if not cloudtrail_findings:
        print("All CloudTrails are logging or no CloudTrails configured.")
    else:
        for f in cloudtrail_findings:
            print(f)
        alert_msg = "CSPM ALERT: CloudTrail Issues:\n" + "\n".join(cloudtrail_findings)
        send_email_alert("CSPM Alert: CloudTrail Issues", alert_msg, "admin@example.com")
        send_slack_alert(alert_msg, slack_webhook)
    ct_file = "logs/cloudtrail_status.csv"
    export_csv([{"CloudTrailIssue": f} for f in cloudtrail_findings], ct_file)
    open_csv_in_excel(ct_file)

    # --- Security Groups ---
    print("\n--- Security Groups (0.0.0.0/0) ---")
    sg_findings = check_security_groups(session)
    if not sg_findings:
        print("No overly permissive Security Groups found.")
    else:
        for f in sg_findings:
            print(f"- {f['GroupId']} allows {f['Protocol']}:{f['Port']} to 0.0.0.0/0 ({f['Description']})")
        alert_msg = "CSPM ALERT: Security Groups open to 0.0.0.0/0:\n"
        for f in sg_findings:
            alert_msg += f"- {f['GroupId']} allows {f['Protocol']}:{f['Port']}\n"
        send_email_alert("CSPM Alert: Security Groups", alert_msg, "admin@example.com")
        send_slack_alert(alert_msg, slack_webhook)
    sg_file = "logs/security_groups.csv"
    export_csv(sg_findings, sg_file)
    open_csv_in_excel(sg_file)

if __name__ == "__main__":
    main()
