from http.server import BaseHTTPRequestHandler
from api._push import json_response, read_json, supabase_request


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_response(self, 204, {})

    def do_POST(self):
        try:
            payload = read_json(self)
            subscription = payload.get("subscription") if isinstance(payload, dict) else None
            if not isinstance(subscription, dict) or not subscription.get("endpoint"):
                json_response(self, 400, {"error": "Assinatura Push inválida."})
                return
            supabase_request(
                "POST", "push_subscriptions",
                {"endpoint": subscription["endpoint"], "subscription": subscription},
                prefer="resolution=merge-duplicates,return=minimal"
            )
            json_response(self, 200, {"ok": True})
        except Exception as error:
            json_response(self, 500, {"error": str(error)})
