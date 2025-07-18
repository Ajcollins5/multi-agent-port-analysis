#!/usr/bin/env python3
"""
Vercel-Compatible Cron Job System
Handles scheduling using Vercel Cron Jobs, external services, and GitHub Actions
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib
import hmac
import logging

class VercelCronManager:
    """Manages cron jobs compatible with Vercel serverless environment"""
    
    def __init__(self):
        self.cron_secret = os.environ.get('CRON_SECRET', 'default_cron_secret')
        if self.cron_secret == 'default_cron_secret':
            logging.warning("CRON_SECRET environment variable not set. Using default value. Set it in Vercel dashboard or local .env for production.")
        self.deployment_url = os.environ.get('VERCEL_URL', '')
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
        self.github_repo = os.environ.get('GITHUB_REPOSITORY', '')
        
        # External cron service configuration
        self.cron_job_org_api_key = os.environ.get('CRON_JOB_ORG_API_KEY', '')
        self.easycron_api_key = os.environ.get('EASYCRON_API_KEY', '')
        
        # In-memory job storage (use database in production)
        self.scheduled_jobs = []
        self.job_history = []
    
    def create_vercel_cron_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Vercel cron job (requires manual vercel.json update)"""
        try:
            # Validate job configuration
            required_fields = ['path', 'schedule', 'name']
            for field in required_fields:
                if field not in job_config:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Generate job ID
            job_id = hashlib.md5(
                f"{job_config['path']}{job_config['schedule']}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:8]
            
            # Create job entry
            job_entry = {
                "job_id": job_id,
                "type": "vercel_cron",
                "path": job_config['path'],
                "schedule": job_config['schedule'],
                "name": job_config['name'],
                "created_at": datetime.now().isoformat(),
                "status": "pending_deployment",
                "metadata": job_config.get('metadata', {})
            }
            
            self.scheduled_jobs.append(job_entry)
            
            # Generate vercel.json configuration
            vercel_config = {
                "path": job_config['path'],
                "schedule": job_config['schedule']
            }
            
            return {
                "success": True,
                "job_id": job_id,
                "message": "Vercel cron job created (requires deployment)",
                "vercel_config": vercel_config,
                "instructions": [
                    "1. Add this configuration to your vercel.json file under 'crons' array",
                    "2. Deploy to Vercel using 'vercel --prod'",
                    "3. The cron job will be automatically scheduled"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_external_cron_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create cron job using external services"""
        try:
            # Try cron-job.org first
            if self.cron_job_org_api_key:
                result = self._create_cron_job_org(job_config)
                if result.get("success"):
                    return result
            
            # Try EasyCron as fallback
            if self.easycron_api_key:
                result = self._create_easycron_job(job_config)
                if result.get("success"):
                    return result
            
            return {
                "success": False,
                "error": "No external cron services configured",
                "required_env_vars": ["CRON_JOB_ORG_API_KEY", "EASYCRON_API_KEY"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_cron_job_org(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create job using cron-job.org API"""
        try:
            # Parse cron schedule
            schedule_parts = self._parse_cron_schedule(job_config['schedule'])
            
            payload = {
                "job": {
                    "url": f"{self.deployment_url}{job_config['path']}",
                    "enabled": True,
                    "schedule": schedule_parts,
                    "requestMethod": "POST",
                    "requestHeaders": [
                        {
                            "name": "Authorization",
                            "value": f"Bearer {self.cron_secret}"
                        },
                        {
                            "name": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "requestBody": json.dumps({
                        "action": "execute_scheduled_job",
                        "job_config": job_config
                    }),
                    "title": job_config.get('name', 'Portfolio Analysis Job'),
                    "saveResponses": True
                }
            }
            
            response = requests.post(
                "https://api.cron-job.org/jobs",
                headers={
                    "Authorization": f"Bearer {self.cron_job_org_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                job_data = response.json()
                
                # Store job information
                job_entry = {
                    "job_id": job_data.get("jobId"),
                    "type": "cron_job_org",
                    "external_id": job_data.get("jobId"),
                    "url": job_data.get("url"),
                    "schedule": job_config['schedule'],
                    "name": job_config['name'],
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "service": "cron-job.org"
                }
                
                self.scheduled_jobs.append(job_entry)
                
                return {
                    "success": True,
                    "job_id": job_data.get("jobId"),
                    "service": "cron-job.org",
                    "message": "Cron job created successfully",
                    "job_url": job_data.get("url")
                }
            else:
                return {
                    "success": False,
                    "error": f"cron-job.org API error: {response.status_code} - {response.text}",
                    "service": "cron-job.org"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "service": "cron-job.org"}
    
    def _create_easycron_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create job using EasyCron API"""
        try:
            payload = {
                "token": self.easycron_api_key,
                "url": f"{self.deployment_url}{job_config['path']}",
                "cron_expression": job_config['schedule'],
                "http_method": "POST",
                "post_data": json.dumps({
                    "action": "execute_scheduled_job",
                    "job_config": job_config
                }),
                "http_headers": json.dumps({
                    "Authorization": f"Bearer {self.cron_secret}",
                    "Content-Type": "application/json"
                }),
                "cron_job_name": job_config.get('name', 'Portfolio Analysis Job'),
                "status": "1"  # Enable job
            }
            
            response = requests.post(
                "https://www.easycron.com/rest/add",
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "success":
                    job_entry = {
                        "job_id": result.get("cron_job_id"),
                        "type": "easycron",
                        "external_id": result.get("cron_job_id"),
                        "schedule": job_config['schedule'],
                        "name": job_config['name'],
                        "created_at": datetime.now().isoformat(),
                        "status": "active",
                        "service": "easycron"
                    }
                    
                    self.scheduled_jobs.append(job_entry)
                    
                    return {
                        "success": True,
                        "job_id": result.get("cron_job_id"),
                        "service": "easycron",
                        "message": "EasyCron job created successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"EasyCron error: {result.get('error', 'Unknown error')}",
                        "service": "easycron"
                    }
            else:
                return {
                    "success": False,
                    "error": f"EasyCron API error: {response.status_code}",
                    "service": "easycron"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "service": "easycron"}
    
    def create_github_actions_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitHub Actions workflow for cron job"""
        try:
            if not self.github_token or not self.github_repo:
                return {
                    "success": False,
                    "error": "GitHub configuration missing",
                    "required_env_vars": ["GITHUB_TOKEN", "GITHUB_REPOSITORY"]
                }
            
            # Generate workflow YAML
            workflow_yaml = self._generate_github_workflow(job_config)
            
            # Create workflow file via GitHub API
            workflow_path = f".github/workflows/{job_config['name'].lower().replace(' ', '-')}.yml"
            
            payload = {
                "message": f"Add cron job: {job_config['name']}",
                "content": workflow_yaml,
                "branch": "main"
            }
            
            response = requests.put(
                f"https://api.github.com/repos/{self.github_repo}/contents/{workflow_path}",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                job_entry = {
                    "job_id": hashlib.md5(workflow_path.encode()).hexdigest()[:8],
                    "type": "github_actions",
                    "workflow_path": workflow_path,
                    "schedule": job_config['schedule'],
                    "name": job_config['name'],
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "service": "github_actions"
                }
                
                self.scheduled_jobs.append(job_entry)
                
                return {
                    "success": True,
                    "job_id": job_entry["job_id"],
                    "service": "github_actions",
                    "workflow_path": workflow_path,
                    "message": "GitHub Actions workflow created"
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}",
                    "service": "github_actions"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "service": "github_actions"}
    
    def _generate_github_workflow(self, job_config: Dict[str, Any]) -> str:
        """Generate GitHub Actions workflow YAML"""
        workflow_name = job_config['name']
        schedule = job_config['schedule']
        path = job_config['path']
        
        yaml_content = f"""name: {workflow_name}

on:
  schedule:
    - cron: '{schedule}'
  workflow_dispatch:

jobs:
  execute-job:
    runs-on: ubuntu-latest
    
    steps:
    - name: Execute {workflow_name}
      run: |
        curl -X POST "${{{{ secrets.VERCEL_DEPLOYMENT_URL }}}}{path}" \\
          -H "Authorization: Bearer ${{{{ secrets.CRON_SECRET }}}}" \\
          -H "Content-Type: application/json" \\
          -d '{{"action": "execute_scheduled_job", "job_config": {json.dumps(job_config)}}}'
    
    - name: Check Response
      run: |
        echo "Job execution completed"
        echo "Timestamp: $(date)"
"""
        
        return yaml_content
    
    def _parse_cron_schedule(self, cron_expression: str) -> Dict[str, Any]:
        """Parse cron expression for cron-job.org API"""
        parts = cron_expression.split()
        
        if len(parts) != 5:
            raise ValueError("Invalid cron expression format")
        
        minute, hour, day, month, weekday = parts
        
        return {
            "timezone": "UTC",
            "minutes": [int(minute)] if minute != "*" else [-1],
            "hours": [int(hour)] if hour != "*" else [-1],
            "mdays": [int(day)] if day != "*" else [-1],
            "months": [int(month)] if month != "*" else [-1],
            "wdays": [int(weekday)] if weekday != "*" else [-1]
        }
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs"""
        return self.scheduled_jobs
    
    def get_job_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get job execution history"""
        return self.job_history[-limit:]
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """Delete a scheduled job"""
        try:
            job = next((j for j in self.scheduled_jobs if j["job_id"] == job_id), None)
            
            if not job:
                return {"success": False, "error": "Job not found"}
            
            # Delete from external service
            if job["type"] == "cron_job_org":
                result = self._delete_cron_job_org(job["external_id"])
            elif job["type"] == "easycron":
                result = self._delete_easycron_job(job["external_id"])
            elif job["type"] == "github_actions":
                result = self._delete_github_workflow(job["workflow_path"])
            else:
                result = {"success": True}
            
            if result.get("success"):
                # Remove from local storage
                self.scheduled_jobs = [j for j in self.scheduled_jobs if j["job_id"] != job_id]
                
                return {
                    "success": True,
                    "message": f"Job {job_id} deleted successfully"
                }
            else:
                return result
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _delete_cron_job_org(self, job_id: str) -> Dict[str, Any]:
        """Delete job from cron-job.org"""
        try:
            response = requests.delete(
                f"https://api.cron-job.org/jobs/{job_id}",
                headers={
                    "Authorization": f"Bearer {self.cron_job_org_api_key}"
                },
                timeout=30
            )
            
            return {"success": response.status_code == 200}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _delete_easycron_job(self, job_id: str) -> Dict[str, Any]:
        """Delete job from EasyCron"""
        try:
            response = requests.post(
                "https://www.easycron.com/rest/delete",
                data={
                    "token": self.easycron_api_key,
                    "id": job_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"success": result.get("status") == "success"}
            
            return {"success": False}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _delete_github_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """Delete GitHub Actions workflow"""
        try:
            # Get file SHA first
            response = requests.get(
                f"https://api.github.com/repos/{self.github_repo}/contents/{workflow_path}",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                file_info = response.json()
                
                # Delete file
                delete_response = requests.delete(
                    f"https://api.github.com/repos/{self.github_repo}/contents/{workflow_path}",
                    headers={
                        "Authorization": f"token {self.github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json={
                        "message": f"Delete workflow: {workflow_path}",
                        "sha": file_info["sha"],
                        "branch": "main"
                    },
                    timeout=30
                )
                
                return {"success": delete_response.status_code == 200}
            
            return {"success": False, "error": "Workflow file not found"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a job (called by cron services)"""
        try:
            start_time = datetime.now()
            
            # Import and execute based on job type
            if job_config.get("job_type") == "portfolio_analysis":
                from ..agents.risk_agent import analyze_portfolio_risk
                result = analyze_portfolio_risk(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"])
            elif job_config.get("job_type") == "risk_assessment":
                from ..agents.risk_agent import analyze_portfolio_risk
                result = analyze_portfolio_risk(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"])
            elif job_config.get("job_type") == "event_monitoring":
                from ..agents.event_sentinel import detect_portfolio_events
                result = detect_portfolio_events(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"])
            else:
                return {"success": False, "error": "Unknown job type"}
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Record execution
            execution_record = {
                "job_id": job_config.get("job_id"),
                "execution_time": start_time.isoformat(),
                "duration": execution_time,
                "result": result,
                "status": "completed" if result.get("success") else "failed"
            }
            
            self.job_history.append(execution_record)
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result": result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all cron services"""
        return {
            "vercel_cron": {
                "available": bool(self.deployment_url),
                "description": "Built-in Vercel cron jobs"
            },
            "cron_job_org": {
                "available": bool(self.cron_job_org_api_key),
                "description": "External cron-job.org service"
            },
            "easycron": {
                "available": bool(self.easycron_api_key),
                "description": "EasyCron external service"
            },
            "github_actions": {
                "available": bool(self.github_token and self.github_repo),
                "description": "GitHub Actions scheduled workflows"
            },
            "total_jobs": len(self.scheduled_jobs),
            "active_jobs": len([j for j in self.scheduled_jobs if j["status"] == "active"])
        }

# Global cron manager instance
cron_manager = VercelCronManager()

def handler(request):
    """Vercel serverless function handler"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "")
            
            # Verify cron secret
            provided_secret = body.get("secret", "") or request.headers.get("Authorization", "").replace("Bearer ", "")
            if provided_secret != cron_manager.cron_secret:
                return json.dumps({"error": "Invalid cron secret", "status": 401})
            
            if action == "create_job":
                job_config = body.get("job_config", {})
                service = body.get("service", "external")
                
                if service == "vercel":
                    return json.dumps(cron_manager.create_vercel_cron_job(job_config))
                elif service == "github":
                    return json.dumps(cron_manager.create_github_actions_job(job_config))
                else:
                    return json.dumps(cron_manager.create_external_cron_job(job_config))
            
            elif action == "execute_scheduled_job":
                job_config = body.get("job_config", {})
                return json.dumps(cron_manager.execute_job(job_config))
            
            elif action == "get_jobs":
                return json.dumps({
                    "success": True,
                    "scheduled_jobs": cron_manager.get_scheduled_jobs()
                })
            
            elif action == "get_history":
                limit = body.get("limit", 20)
                return json.dumps({
                    "success": True,
                    "job_history": cron_manager.get_job_history(limit)
                })
            
            elif action == "delete_job":
                job_id = body.get("job_id", "")
                return json.dumps(cron_manager.delete_job(job_id))
            
            elif action == "get_status":
                return json.dumps(cron_manager.get_service_status())
            
            else:
                return json.dumps({"error": "Unknown action"})
        
        elif request.method == "GET":
            return json.dumps(cron_manager.get_service_status())
        
        else:
            return json.dumps({"error": "Method not allowed"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Test the cron manager
    manager = VercelCronManager()
    print("Cron Manager Status:")
    print(json.dumps(manager.get_service_status(), indent=2)) 