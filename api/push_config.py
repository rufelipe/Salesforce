from http.server import BaseHTTPRequestHandler
import os

from api._push import json_response


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = os.environ.get("VAPID_PUBLIC_KEY", "").strip()
        if not key:
            json_response(self, 503, {"error": "Configure VAPID_PUBLIC_KEY na Vercel."})
            return
        json_response(self, 200, {"public_key": key})
