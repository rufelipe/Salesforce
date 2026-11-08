import json
import os
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen

from pywebpush import WebPushException, webpush

from api._push import env, json_response, supabase_request


class handler:
    def do_GET(self):
        self._run()

    def do_POST(self):
        self._run()

    def _run(self):
        supplied = self.headers.get("Authorization", "")
        secret = os.environ.get("CRON_SECRET", "")
        if not secret or supplied != "Bearer " + secret:
            json_response(self, 401, {"error": "Não autorizado."})
            return
        try:
            now = datetime.now(timezone.utc).isoformat()
            pending = supabase_request(
                "GET", "yoda_reminders",
                query="select=*&sent_at=is.null&remind_at=lte." + quote(now, safe=":+.-TZ")
            )
            subscriptions = supabase_request("GET", "push_subscriptions", query="select=*")
            sent = 0
            failed = 0
            for reminder in pending:
                payload = {
                    "title": "Lembrete do YODA",
                    "body": (reminder.get("title") or "Compromisso") +
                            ((" • Contrato " + reminder["contract"]) if reminder.get("contract") else "") +
                            " começa em breve.",
                    "url": reminder.get("open_url") or "/",
                    "tag": "yoda-" + str(reminder.get("task_id", "")),
                }
                expired = []
                for item in subscriptions:
                    try:
                        webpush(
                            subscription_info=item["subscription"],
                            data=json.dumps(payload, ensure_ascii=False),
                            vapid_private_key=env("VAPID_PRIVATE_KEY"),
                            vapid_claims={"sub": env("VAPID_SUBJECT")}
                        )
                    except WebPushException as error:
                        status = getattr(getattr(error, "response", None), "status_code", None)
                        if status in (404, 410):
                            expired.append(item.get("endpoint"))
                        failed += 1
                    except Exception:
                        failed += 1
                for endpoint in expired:
                    supabase_request("DELETE", "push_subscriptions",
                                     query="endpoint=eq." + quote(endpoint, safe=""))
                if subscriptions and not expired and failed == 0:
                    supabase_request(
                        "PATCH", "yoda_reminders",
                        {"sent_at": datetime.now(timezone.utc).isoformat()},
                        query="task_id=eq." + quote(str(reminder["task_id"]), safe="")
                    )
                    sent += 1
            json_response(self, 200, {"ok": True, "due": len(pending), "sent": sent, "failed": failed})
        except Exception as error:
            json_response(self, 500, {"error": str(error)})
