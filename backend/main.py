from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import json

from services.aws_service import (
    verify_credentials, get_regions, scan_ec2,
    scan_ebs, scan_rds, scan_s3, get_monthly_cost
)
from services.optimizer import run_all_checks
from services.ai_service import generate_recommendations, chat_with_ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Cost Optimizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────────────────────────

class AWSCredentials(BaseModel):
    access_key: str
    secret_key: str
    region: Optional[str] = None   # optional — auto-detected if omitted

class ChatRequest(BaseModel):
    message: str
    access_key: str
    secret_key: str
    history: Optional[list] = []


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-cost-optimizer"}


# ── AWS Connection ─────────────────────────────────────────────────────────────

@app.post("/connect")
def connect_aws(creds: AWSCredentials):
    logger.info(json.dumps({"event": "connect_attempt"}))
    try:
        identity = verify_credentials(creds.access_key, creds.secret_key)
        regions = get_regions(creds.access_key, creds.secret_key)

        # Auto-detect: prefer the region the caller supplied, otherwise
        # pick the first enabled region returned by EC2 describe-regions.
        detected_region = creds.region if creds.region else (regions[0] if regions else "us-east-1")

        logger.info(json.dumps({"event": "connect_success", "account": identity["Account"], "region": detected_region}))
        return {
            "account_id": identity["Account"],
            "arn": identity["Arn"],
            "region": detected_region,
            "regions": regions,
        }
    except Exception as e:
        logger.error(json.dumps({"event": "connect_failed", "error": str(e)}))
        raise HTTPException(status_code=401, detail="Invalid AWS credentials")


# ── Full Scan ─────────────────────────────────────────────────────────────────

@app.post("/scan")
def full_scan(creds: AWSCredentials):
    logger.info(json.dumps({"event": "scan_started"}))
    try:
        ak, sk, region = creds.access_key, creds.secret_key, creds.region or "us-east-1"

        ec2_instances = scan_ec2(ak, sk, region)
        ebs_volumes   = scan_ebs(ak, sk, region)
        rds_instances = scan_rds(ak, sk, region)
        s3_buckets    = scan_s3(ak, sk)
        monthly_cost  = get_monthly_cost(ak, sk)

        recommendations = run_all_checks(ec2_instances, ebs_volumes, rds_instances)

        total_saving = sum(r.get("saving", 0) for r in recommendations)

        logger.info(json.dumps({
            "event": "scan_completed",
            "ec2": len(ec2_instances),
            "ebs": len(ebs_volumes),
            "rds": len(rds_instances),
            "s3": len(s3_buckets),
            "recommendations": len(recommendations)
        }))

        return {
            "monthly_cost": monthly_cost,
            "potential_saving": total_saving,
            "resources": {
                "ec2": ec2_instances,
                "ebs": ebs_volumes,
                "rds": rds_instances,
                "s3": s3_buckets,
            },
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(json.dumps({"event": "scan_failed", "error": str(e)}))
        raise HTTPException(status_code=500, detail=str(e))


# ── AI Recommendations ────────────────────────────────────────────────────────

@app.post("/analyze")
def ai_analyze(creds: AWSCredentials):
    logger.info(json.dumps({"event": "ai_analyze_started"}))
    try:
        ak, sk, region = creds.access_key, creds.secret_key, creds.region or "us-east-1"

        ec2 = scan_ec2(ak, sk, region)
        ebs = scan_ebs(ak, sk, region)
        rds = scan_rds(ak, sk, region)
        cost = get_monthly_cost(ak, sk)

        scan_summary = {
            "monthly_cost": cost,
            "ec2_instances": ec2,
            "ebs_volumes": ebs,
            "rds_instances": rds,
        }

        analysis = generate_recommendations(scan_summary)
        logger.info(json.dumps({"event": "ai_analyze_completed"}))
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Chatbot ───────────────────────────────────────────────────────────────────

@app.post("/chat")
def chat(req: ChatRequest):
    logger.info(json.dumps({"event": "chat_message", "message_length": len(req.message)}))
    try:
        context = ""
        if req.access_key and req.secret_key:
            try:
                identity = verify_credentials(req.access_key, req.secret_key)
                cost = get_monthly_cost(req.access_key, req.secret_key)
                context = f"AWS Account: {identity['Account']}, Current monthly cost: ${cost:.2f}. "
            except Exception:
                pass

        answer = chat_with_ai(req.message, req.history, context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
