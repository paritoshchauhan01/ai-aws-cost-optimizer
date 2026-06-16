"""
Cost optimization rules.
Each function returns a list of recommendation dicts:
  { resource_id, resource_type, issue, action, saving (USD/month estimate) }
"""

LARGE_INSTANCE_TYPES = {
    "t3.large", "t3.xlarge", "t3.2xlarge",
    "m5.large", "m5.xlarge", "m5.2xlarge", "m5.4xlarge",
    "c5.large", "c5.xlarge", "c5.2xlarge",
    "r5.large", "r5.xlarge",
}

DOWNSIZE_SAVINGS = {
    "t3.large": 30, "t3.xlarge": 60, "t3.2xlarge": 120,
    "m5.large": 35, "m5.xlarge": 70, "m5.2xlarge": 140, "m5.4xlarge": 280,
    "c5.large": 30, "c5.xlarge": 60, "c5.2xlarge": 120,
    "r5.large": 45, "r5.xlarge": 90,
}


def check_idle_ec2(instances: list) -> list:
    recs = []
    for i in instances:
        if i["state"] == "stopped":
            recs.append({
                "resource_id": i["id"],
                "resource_name": i.get("name", i["id"]),
                "resource_type": "EC2",
                "issue": "Instance is stopped but still incurring EBS costs",
                "action": "Terminate if no longer needed or create an AMI first",
                "saving": 5,
            })
        elif i["type"] in LARGE_INSTANCE_TYPES and i["state"] == "running":
            saving = DOWNSIZE_SAVINGS.get(i["type"], 30)
            recs.append({
                "resource_id": i["id"],
                "resource_name": i.get("name", i["id"]),
                "resource_type": "EC2",
                "issue": f"Large instance type {i['type']} — may be oversized",
                "action": f"Review CPU/memory usage; downsize to a smaller type",
                "saving": saving,
            })
    return recs


def check_unattached_ebs(volumes: list) -> list:
    recs = []
    for v in volumes:
        if not v["attached"]:
            # gp2: ~$0.10/GB/month, gp3: ~$0.08
            rate = 0.10 if v["type"] in ("gp2", "io1", "io2") else 0.08
            saving = round(v["size_gb"] * rate, 2)
            recs.append({
                "resource_id": v["id"],
                "resource_name": v.get("name", v["id"]),
                "resource_type": "EBS",
                "issue": f"Unattached {v['size_gb']}GB {v['type']} volume",
                "action": "Create a snapshot and delete the volume",
                "saving": saving,
            })
    return recs


def check_oversized_rds(instances: list) -> list:
    recs = []
    large_classes = {"db.m5.large", "db.m5.xlarge", "db.m5.2xlarge",
                     "db.r5.large", "db.r5.xlarge", "db.t3.large"}
    for db in instances:
        if db["class"] in large_classes:
            recs.append({
                "resource_id": db["id"],
                "resource_name": db["id"],
                "resource_type": "RDS",
                "issue": f"Large RDS class {db['class']} — review actual utilisation",
                "action": "Check CPU/connection metrics; downsize or switch to Aurora Serverless",
                "saving": 50,
            })
        if not db["multi_az"] and db["status"] == "available":
            # Not a cost saving but a reliability note — skip for cost report
            pass
    return recs


def run_all_checks(ec2: list, ebs: list, rds: list) -> list:
    recs = []
    recs.extend(check_idle_ec2(ec2))
    recs.extend(check_unattached_ebs(ebs))
    recs.extend(check_oversized_rds(rds))
    return recs
