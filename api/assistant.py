import re

from api._data import APIHandler, notes, tasks


class handler(APIHandler):
    def do_POST(self):
        try:
            payload = self.read_json()
        except (ValueError, TypeError) as error:
            self.send_json(400, {"error": str(error)})
            return

        if not isinstance(payload, dict):
            self.send_json(400, {"error": "O corpo precisa ser um objeto JSON."})
            return
        question = str(payload.get("question", "")).strip()
        if not question:
            self.send_json(400, {"error": "Informe a pergunta no campo 'question'."})
            return

        all_tasks = tasks()
        all_notes = notes()
        numbers = re.findall(r"\d+", question)
        if numbers:
            terms = numbers
        else:
            ignored = {"qual", "quais", "mostre", "buscar", "busque", "detalhe", "detalhes",
                       "sobre", "contrato", "tarefa", "tarefas", "anotacao", "anotacoes",
                       "para", "com", "uma", "por", "do", "da", "de", "o", "a", "me"}
            terms = [word for word in re.findall(r"[\wÀ-ÿ]+", question.lower())
                     if word not in ignored and len(word) > 1]

        matching_tasks = [item for item in all_tasks if any(
            term.lower() in " ".join(str(value) for value in item.values()).lower()
            for term in terms
        )]
        matching_notes = [item for item in all_notes if any(
            term.lower() in (item.get("contact", "") + " " + item.get("text", "")).lower()
            for term in terms
        )]
        self.send_json(200, {
            "question": question,
            "answer": "Encontrei registros relacionados." if matching_tasks or matching_notes
                      else "Não encontrei tarefas ou anotações para essa pergunta.",
            "tasks": matching_tasks,
            "notes": matching_notes,
        })
