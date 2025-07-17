import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Environment variables
VERCEL_DEPLOYMENT_URL = os.environ.get("VERCEL_URL", "")
CRON_SECRET = os.environ.get("CRON_SECRET", "default_secret")

# In-memory storage for scheduled jobs
SCHEDULED_JOBS = []
JOB_HISTORY = []

def schedule_portfolio_analysis(interval_minutes: int = 60) -> Dict[str, Any]:
    """Schedule portfolio analysis to run at specified intervals"""
    try:
        job_id = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        scheduled_job = {
            "job_id": job_id,
            "type": "portfolio_analysis",
            "interval_minutes": interval_minutes,
            "next_run": (datetime.now() + timedelta(minutes=interval_minutes)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "run_count": 0
        }
        
        SCHEDULED_JOBS.append(scheduled_job)
        
        return {
            "success": True,
            "job_id": job_id,
            "scheduled_for": scheduled_job["next_run"],
            "interval_minutes": interval_minutes,
            "message": f"Portfolio analysis scheduled to run every {interval_minutes} minutes"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_scheduled_job(job_id: str) -> Dict[str, Any]:
    """Execute a scheduled job"""
    try:
        # Find the job
        job = None
        for scheduled_job in SCHEDULED_JOBS:
            if scheduled_job["job_id"] == job_id:
                job = scheduled_job
                break
        
        if not job:
            return {"success": False, "error": f"Job {job_id} not found"}
        
        # Execute based on job type
        if job["type"] == "portfolio_analysis":
            result = execute_portfolio_analysis()
        elif job["type"] == "risk_assessment":
            result = execute_risk_assessment()
        elif job["type"] == "event_monitoring":
            result = execute_event_monitoring()
        else:
            return {"success": False, "error": f"Unknown job type: {job['type']}"}
        
        # Update job status
        job["run_count"] += 1
        job["last_run"] = datetime.now().isoformat()
        job["next_run"] = (datetime.now() + timedelta(minutes=job["interval_minutes"])).isoformat()
        job["status"] = "completed" if result["success"] else "failed"
        
        # Add to history
        JOB_HISTORY.append({
            "job_id": job_id,
            "execution_time": datetime.now().isoformat(),
            "result": result,
            "duration": result.get("duration", 0)
        })
        
        return {
            "success": True,
            "job_id": job_id,
            "execution_result": result,
            "next_run": job["next_run"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "job_id": job_id}

def execute_portfolio_analysis() -> Dict[str, Any]:
    """Execute portfolio analysis by calling the risk agent"""
    try:
        start_time = datetime.now()
        
        # Call risk agent for portfolio analysis
        portfolio = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]  # Default portfolio
        
        # Simulate API call to risk agent (in production, use actual API)
        # In Vercel environment, this would be an internal API call
        analysis_result = {
            "portfolio_size": len(portfolio),
            "analyzed_stocks": len(portfolio),
            "high_risk_count": 1,  # Simulated
            "portfolio_risk": "MEDIUM",
            "timestamp": datetime.now().isoformat()
        }
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "type": "portfolio_analysis",
            "result": analysis_result,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "type": "portfolio_analysis"}

def execute_risk_assessment() -> Dict[str, Any]:
    """Execute risk assessment"""
    try:
        start_time = datetime.now()
        
        # Simulate risk assessment
        risk_result = {
            "overall_risk": "MEDIUM",
            "high_risk_stocks": 1,
            "risk_factors": ["Market volatility", "Sector rotation"],
            "timestamp": datetime.now().isoformat()
        }
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "type": "risk_assessment",
            "result": risk_result,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "type": "risk_assessment"}

def execute_event_monitoring() -> Dict[str, Any]:
    """Execute event monitoring"""
    try:
        start_time = datetime.now()
        
        # Simulate event monitoring
        event_result = {
            "events_detected": 3,
            "high_priority_events": 1,
            "event_types": ["price_movement", "volume_spike", "news_event"],
            "timestamp": datetime.now().isoformat()
        }
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "type": "event_monitoring",
            "result": event_result,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "type": "event_monitoring"}

def get_scheduled_jobs() -> Dict[str, Any]:
    """Get all scheduled jobs"""
    return {
        "scheduled_jobs": SCHEDULED_JOBS,
        "total_jobs": len(SCHEDULED_JOBS),
        "active_jobs": len([job for job in SCHEDULED_JOBS if job["status"] == "scheduled"]),
        "timestamp": datetime.now().isoformat()
    }

def get_job_history(limit: int = 10) -> Dict[str, Any]:
    """Get job execution history"""
    return {
        "job_history": JOB_HISTORY[-limit:],
        "total_executions": len(JOB_HISTORY),
        "timestamp": datetime.now().isoformat()
    }

def cancel_job(job_id: str) -> Dict[str, Any]:
    """Cancel a scheduled job"""
    try:
        for i, job in enumerate(SCHEDULED_JOBS):
            if job["job_id"] == job_id:
                job["status"] = "cancelled"
                return {
                    "success": True,
                    "message": f"Job {job_id} cancelled successfully"
                }
        
        return {"success": False, "error": f"Job {job_id} not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_cron_job(job_type: str, interval_minutes: int, job_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new cron job"""
    try:
        job_id = f"{job_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if job_config is None:
            job_config = {}
        
        scheduled_job = {
            "job_id": job_id,
            "type": job_type,
            "interval_minutes": interval_minutes,
            "next_run": (datetime.now() + timedelta(minutes=interval_minutes)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "run_count": 0,
            "config": job_config
        }
        
        SCHEDULED_JOBS.append(scheduled_job)
        
        return {
            "success": True,
            "job_id": job_id,
            "job_type": job_type,
            "scheduled_for": scheduled_job["next_run"],
            "interval_minutes": interval_minutes
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_and_execute_due_jobs() -> Dict[str, Any]:
    """Check for due jobs and execute them"""
    try:
        current_time = datetime.now()
        executed_jobs = []
        
        for job in SCHEDULED_JOBS:
            if job["status"] == "scheduled":
                next_run_time = datetime.fromisoformat(job["next_run"])
                
                if current_time >= next_run_time:
                    execution_result = execute_scheduled_job(job["job_id"])
                    executed_jobs.append(execution_result)
        
        return {
            "success": True,
            "executed_jobs": len(executed_jobs),
            "results": executed_jobs,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def handler(request):
    """Vercel serverless function handler for cron jobs"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "check_jobs")
            
            # Verify cron secret for security
            provided_secret = body.get("secret", "") or request.headers.get("X-Cron-Secret", "")
            if provided_secret != CRON_SECRET:
                return json.dumps({"error": "Invalid cron secret", "status": 401})
            
            if action == "check_jobs":
                return json.dumps(check_and_execute_due_jobs())
            
            elif action == "schedule_portfolio":
                interval = body.get("interval_minutes", 60)
                return json.dumps(schedule_portfolio_analysis(interval))
            
            elif action == "create_job":
                job_type = body.get("job_type", "portfolio_analysis")
                interval = body.get("interval_minutes", 60)
                config = body.get("config", {})
                return json.dumps(create_cron_job(job_type, interval, config))
            
            elif action == "execute_job":
                job_id = body.get("job_id", "")
                return json.dumps(execute_scheduled_job(job_id))
            
            elif action == "cancel_job":
                job_id = body.get("job_id", "")
                return json.dumps(cancel_job(job_id))
            
            elif action == "get_jobs":
                return json.dumps(get_scheduled_jobs())
            
            elif action == "get_history":
                limit = body.get("limit", 10)
                return json.dumps(get_job_history(limit))
            
            else:
                return json.dumps({
                    "error": "Invalid action",
                    "available_actions": [
                        "check_jobs", "schedule_portfolio", "create_job",
                        "execute_job", "cancel_job", "get_jobs", "get_history"
                    ]
                })
        
        else:
            return json.dumps({
                "service": "CronHandler",
                "description": "Handles background scheduling for portfolio analysis",
                "endpoints": [
                    "POST - check_jobs: Check and execute due jobs",
                    "POST - schedule_portfolio: Schedule portfolio analysis",
                    "POST - create_job: Create new cron job",
                    "POST - execute_job: Execute specific job",
                    "POST - cancel_job: Cancel scheduled job",
                    "POST - get_jobs: Get all scheduled jobs",
                    "POST - get_history: Get job execution history"
                ],
                "status": "active",
                "note": "Requires X-Cron-Secret header or secret in request body"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "service": "CronHandler"}) 