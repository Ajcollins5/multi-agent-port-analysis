import json
import os
import asyncio
from datetime import datetime

async def get_enhanced_health():
    """Get enhanced health check with monitoring"""
    try:
        from monitoring.health_monitor import health_monitor

        # Get comprehensive system health
        system_health = await health_monitor.get_system_health()

        # Add environment configuration check
        environment_config = {
            "supabase_url_configured": bool(os.environ.get("SUPABASE_URL")),
            "postgres_url_configured": bool(os.environ.get("POSTGRES_URL")),
            "service_role_configured": bool(os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
        }

        return {
            "success": True,
            "status": system_health["overall_status"],
            "timestamp": datetime.now().isoformat(),
            "components": system_health["components"],
            "environment": environment_config,
            "checks_completed": system_health["checks_completed"]
        }

    except Exception as e:
        # Fallback to basic health check
        return {
            "success": False,
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": f"Health monitoring failed: {str(e)}",
            "message": "Fallback health check"
        }

def handler(event, context):
    """Enhanced health check function with comprehensive monitoring"""
    try:
        # Try to run enhanced health check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        health_data = loop.run_until_complete(get_enhanced_health())
        loop.close()

        status_code = 200 if health_data.get("success") else 503

        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(health_data)
        }

    except Exception as e:
        # Ultra-minimal fallback
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "status": "basic",
                "timestamp": datetime.now().isoformat(),
                "message": "Minimal function working",
                "error": str(e)
            })
        }