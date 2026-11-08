from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
from urllib.parse import parse_qs
from zoneinfo import ZoneInfo

from api._push import json_response, read_json, supabase_request


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_response(self, 204, {})

    def do_DELETE(self):
        try:
            params = parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            task_id = (params.get("task_id") or [""])[0].strip()
            if not task_id:
                json_response(self, 400, {"error": "Informe task_id."})
                return
            from urllib.parse import quote
            supabase_request("DELETE", "yoda_reminders",
                             query="task_id=eq." + quote(task_id, safe=""))
            json_response(self, 200, {"ok": True})
        except Exception as error:
            json_response(self, 500, {"error": str(error)})

    def do_POST(self):
        try:
            payload = read_json(self)
            if not isinstance(payload, dict):
                json_response(self, 400, {"error": "Envie um objeto JSON."})
                return
            task_id = str(payload.get("task_id", "")).strip()
            title = str(payload.get("title", "Compromisso Salesforce")).strip()
            starts_at = str(payload.get("starts_at", "")).strip()
            if not task_id:
                json_response(self, 400, {"error": "task_id é obrigatório."})
                return
            if payload.get("cancel") or not starts_at:
                from urllib.parse import quote
                supabase_request("DELETE", "yoda_reminders",
                                 query="task_id=eq." + quote(task_id, safe=""))
                json_response(self, 200, {"ok": True, "cancelled": True})
                return
            start = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
            if start.tzinfo is None:
                start = start.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            reminder = start - timedelta(minutes=5)
            record = {
                "task_id": task_id,
                "title": title[:240],
                "contract": str(payload.get("contract", ""))[:80],
                "starts_at": start.isoformat(),
                "remind_at": reminder.isoformat(),
                "open_url": str(payload.get("open_url", "/"))[:500],
                "sent_at": None,
            }
            supabase_request(
                "POST", "yoda_reminders", record,
                prefer="resolution=merge-duplicates,return=minimal"
            )
            json_response(self, 200, {"ok": True, "remind_at": reminder.isoformat()})
        except Exception as error:
            json_response(self, 500, {"error": str(error)})
