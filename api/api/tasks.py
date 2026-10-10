import json

from api._data import APIHandler, tasks


class handler(APIHandler):
    def do_GET(self):
        self.send_json(200, tasks())

    def do_POST(self):
        try:
            task = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
            return
        if not isinstance(task, dict):
            self.send_json(400, {"error": "O corpo precisa ser um objeto JSON."})
            return
        required = ("title", "contract", "due", "status")
        missing = [field for field in required if not task.get(field)]
        if missing:
            self.send_json(400, {"error": "Campos obrigatórios ausentes: " + ", ".join(missing)})
            return
        task.setdefault("response", "Nenhum")
        task.setdefault("related", "")
        task.setdefault("observation", "")
        task.setdefault("priority", "Normal")
        task.setdefault("stage", "Sem etapa")
        self.send_json(201, task)
