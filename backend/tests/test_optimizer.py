"""
Basic tests for the optimizer rules.
Run with: pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.optimizer import check_idle_ec2, check_unattached_ebs, check_oversized_rds, run_all_checks


def test_stopped_ec2_flagged():
    instances = [{"id": "i-123", "name": "test", "type": "t3.medium", "state": "stopped"}]
    recs = check_idle_ec2(instances)
    assert len(recs) == 1
    assert recs[0]["resource_id"] == "i-123"
    assert recs[0]["resource_type"] == "EC2"


def test_running_small_ec2_not_flagged():
    instances = [{"id": "i-456", "name": "small", "type": "t3.micro", "state": "running"}]
    recs = check_idle_ec2(instances)
    assert len(recs) == 0


def test_large_ec2_flagged():
    instances = [{"id": "i-789", "name": "big", "type": "t3.large", "state": "running"}]
    recs = check_idle_ec2(instances)
    assert len(recs) == 1
    assert recs[0]["saving"] > 0


def test_unattached_ebs_flagged():
    volumes = [{"id": "vol-001", "name": "", "size_gb": 50, "type": "gp2", "state": "available", "attached": False}]
    recs = check_unattached_ebs(volumes)
    assert len(recs) == 1
    assert recs[0]["saving"] == 5.0


def test_attached_ebs_not_flagged():
    volumes = [{"id": "vol-002", "name": "", "size_gb": 50, "type": "gp2", "state": "in-use", "attached": True}]
    recs = check_unattached_ebs(volumes)
    assert len(recs) == 0


def test_run_all_checks_combined():
    ec2 = [{"id": "i-1", "name": "", "type": "t3.large", "state": "running"}]
    ebs = [{"id": "vol-1", "name": "", "size_gb": 100, "type": "gp2", "state": "available", "attached": False}]
    rds = []
    recs = run_all_checks(ec2, ebs, rds)
    assert len(recs) == 2
