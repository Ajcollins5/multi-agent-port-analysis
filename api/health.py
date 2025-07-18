import json
from datetime import datetime

def handler(event, context):
    """Ultra-minimal health check function"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": True,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "Minimal function working"
        })
    } 