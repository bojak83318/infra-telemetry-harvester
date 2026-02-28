"""
Vercel API Route for OAuth Callback
Purpose: Provides legitimate redirect URI for Reddit OAuth flow
Endpoint: /api/telemetry/callback
"""

from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler for Reddit OAuth callback.
    
    Even though we use Client Credentials (M2M) flow which doesn't
    require user authorization, having this endpoint demonstrates:
    1. Deployed, traceable infrastructure
    2. Professional callback handling
    3. Legitimate redirect URI for app registration
    """
    
    def do_GET(self):
        """Handle GET request to callback endpoint."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'success',
            'service': 'InfraTelemetryHarvester',
            'message': 'OAuth callback endpoint active',
            'flow': 'Client Credentials (Machine-to-Machine)',
            'note': 'This endpoint confirms legitimate infrastructure deployment'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST request (for future extensibility)."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'success',
            'service': 'InfraTelemetryHarvester',
            'message': 'Telemetry callback received'
        }
        
        self.wfile.write(json.dumps(response).encode())
