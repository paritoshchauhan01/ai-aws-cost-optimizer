import boto3
from datetime import datetime, timedelta, timezone


def _ec2(access_key, secret_key, region):
    return boto3.client(
        "ec2",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def _rds(access_key, secret_key, region):
    return boto3.client(
        "rds",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def _s3(access_key, secret_key):
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def _ce(access_key, secret_key):
    return boto3.client(
        "ce",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
    )


# ── Credential verify ─────────────────────────────────────────────────────────

def verify_credentials(access_key, secret_key):
    sts = boto3.client(
        "sts",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return sts.get_caller_identity()


# ── Regions ───────────────────────────────────────────────────────────────────

def get_regions(access_key, secret_key):
    client = _ec2(access_key, secret_key, "us-east-1")
    resp = client.describe_regions(Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}])
    return [r["RegionName"] for r in resp["Regions"]]


# ── EC2 ───────────────────────────────────────────────────────────────────────

def scan_ec2(access_key, secret_key, region):
    client = _ec2(access_key, secret_key, region)
    resp = client.describe_instances()
    instances = []
    for reservation in resp.get("Reservations", []):
        for i in reservation.get("Instances", []):
            if i["State"]["Name"] == "terminated":
                continue
            name = ""
            for tag in i.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
            instances.append({
                "id": i["InstanceId"],
                "name": name,
                "type": i["InstanceType"],
                "state": i["State"]["Name"],
                "region": region,
                "launch_time": str(i.get("LaunchTime", "")),
            })
    return instances


# ── EBS ───────────────────────────────────────────────────────────────────────

def scan_ebs(access_key, secret_key, region):
    client = _ec2(access_key, secret_key, region)
    resp = client.describe_volumes()
    volumes = []
    for v in resp.get("Volumes", []):
        name = ""
        for tag in v.get("Tags", []):
            if tag["Key"] == "Name":
                name = tag["Value"]
        volumes.append({
            "id": v["VolumeId"],
            "name": name,
            "size_gb": v["Size"],
            "state": v["State"],
            "type": v["VolumeType"],
            "attached": len(v.get("Attachments", [])) > 0,
            "region": region,
        })
    return volumes


# ── RDS ───────────────────────────────────────────────────────────────────────

def scan_rds(access_key, secret_key, region):
    client = _rds(access_key, secret_key, region)
    resp = client.describe_db_instances()
    instances = []
    for db in resp.get("DBInstances", []):
        instances.append({
            "id": db["DBInstanceIdentifier"],
            "engine": db["Engine"],
            "class": db["DBInstanceClass"],
            "status": db["DBInstanceStatus"],
            "storage_gb": db["AllocatedStorage"],
            "multi_az": db["MultiAZ"],
            "region": region,
        })
    return instances


# ── S3 ────────────────────────────────────────────────────────────────────────

def scan_s3(access_key, secret_key):
    client = _s3(access_key, secret_key)
    resp = client.list_buckets()
    buckets = []
    for b in resp.get("Buckets", []):
        buckets.append({
            "name": b["Name"],
            "created": str(b.get("CreationDate", "")),
        })
    return buckets


# ── Cost Explorer ─────────────────────────────────────────────────────────────

def get_monthly_cost(access_key, secret_key):
    client = _ce(access_key, secret_key)
    today = datetime.now(timezone.utc)
    start = today.replace(day=1).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    # Avoid start == end (first day of month edge case)
    if start == end:
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        resp = client.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
        )
        amount = resp["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
        return round(float(amount), 2)
    except Exception:
        return 0.0
