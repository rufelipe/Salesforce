from datetime import datetime
import json
import os
from urllib.request import Request, urlopen




class CRMAdapter:
    """Contrato comum: cada integração deve retornar tarefas e anotações normalizadas."""


    def buscar_tarefas(self):
        raise NotImplementedError


    def buscar_anotacoes(self):
        raise NotImplementedError




class RESTCRMAdapter(CRMAdapter):
    """Adaptador básico para APIs REST que usam JSON e token Bearer."""


    def __init__(self, config):
        self.config = config
        self.base_url = config["base_url"].rstrip("/") + "/"
        self.token = os.environ.get(config.get("token_env", "CRM_API_TOKEN"))
        if not self.token:
            raise ValueError("Configure o token da API na variável de ambiente indicada.")


    def _buscar_registros(self, endpoint, collection_key):
        url = self.base_url + endpoint.lstrip("/")
        request = Request(url, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
        })
        with urlopen(request, timeout=15) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))


        if collection_key:
            for parte in collection_key.split("."):
                dados = dados[parte]
        if not isinstance(dados, list):
            raise ValueError("A resposta da API precisa conter uma lista de registros.")
        return dados


    @staticmethod
    def _valor(registro, caminho):
        valor = registro
        for parte in caminho.split("."):
            if not isinstance(valor, dict):
                return ""
            valor = valor.get(parte, "")
        return "" if valor is None else str(valor)


    def _normalizar(self, registros, campos):
        return [
            dict((nome, self._valor(registro, caminho))
                 for nome, caminho in campos.items())
            for registro in registros
        ]


    def buscar_tarefas(self):
        config = self.config["tarefas"]
        registros = self._buscar_registros(
            config["endpoint"], config.get("collection_key", "")
        )
        return self._normalizar(registros, config["campos"])


    def buscar_anotacoes(self):
        config = self.config["anotacoes"]
        registros = self._buscar_registros(
            config["endpoint"], config.get("collection_key", "")
        )
        return self._normalizar(registros, config["campos"])




class SalesforceDemoAdapter(CRMAdapter):
    """CRM fictício offline com registros inspirados na tela do Salesforce."""


    def __init__(self):
        self.tarefas = [
            {
                "titulo": "Tarefa com contato: Reforço de reparos e benfeitorias - IQ",
                "responsavel": "Rudson Felipe Moreira", "prazo": "2026-11-05",
                "status": "em andamento", "etapa": "Pré Saída IQ",
                "contrato": "773174", "resposta": "Nenhum",
                "observacao": "Sem sucesso; encaminhado o pitch.",
                "prioridade": "Normal", "relacionado": "01430926",
            },
            {
                "titulo": "Tarefa com contato: Reforço de reparos e benfeitorias - IQ",
                "responsavel": "Marina Costa", "prazo": "2026-11-01",
                "status": "em andamento", "etapa": "Pré Saída IQ",
                "contrato": "996334", "resposta": "Nenhum",
                "observacao": "Cliente pediu retorno sobre a proposta.",
                "prioridade": "Normal", "relacionado": "01430927",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "Rafael Souza",
                "prazo": "2099-09-30", "status": "em andamento",
                "etapa": "Retenção", "contrato": "106893",
                "resposta": "Retornar contato", "observacao": "Ligação sem sucesso.",
                "prioridade": "Alta", "relacionado": "01430928",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "Marina Costa",
                "prazo": "2099-09-30", "status": "em andamento",
                "etapa": "Retenção", "contrato": "996334",
                "resposta": "Nenhum", "observacao": "Aguardando resposta do cliente.",
                "prioridade": "Normal", "relacionado": "01430929",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "Rudson Felipe Moreira",
                "prazo": "2099-10-05", "status": "em andamento",
                "etapa": "Retenção", "contrato": "853514",
                "resposta": "Retornar contato", "observacao": "Nova tentativa agendada.",
                "prioridade": "Normal", "relacionado": "01430930",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "João Lima",
                "prazo": "2099-10-05", "status": "em andamento",
                "etapa": "Retenção", "contrato": "108846",
                "resposta": "Nenhum", "observacao": "Cliente ainda avaliando as opções.",
                "prioridade": "Baixa", "relacionado": "01430931",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "Marina Costa",
                "prazo": "2099-10-06", "status": "em andamento",
                "etapa": "Retenção", "contrato": "412144",
                "resposta": "Retornar contato", "observacao": "Deixar mensagem ao cliente.",
                "prioridade": "Normal", "relacionado": "01430932",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "Rafael Souza",
                "prazo": "2099-10-07", "status": "em andamento",
                "etapa": "Retenção", "contrato": "119755",
                "resposta": "Nenhum", "observacao": "Aguardando confirmação.",
                "prioridade": "Normal", "relacionado": "01430933",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "João Lima",
                "prazo": "2099-10-11", "status": "em andamento",
                "etapa": "Retenção", "contrato": "113551",
                "resposta": "Retornar contato", "observacao": "Contato realizado; sem retorno.",
                "prioridade": "Alta", "relacionado": "01430934",
            },
            {
                "titulo": "Retenção - PP", "responsavel": "Marina Costa",
                "prazo": "data-invalida", "status": "não iniciado",
                "etapa": "Retenção", "contrato": "538496",
                "resposta": "Nenhum", "observacao": "Tarefa ainda não iniciada.",
                "prioridade": "Normal", "relacionado": "01430935",
            },
        ]
        self.anotacoes = [
            {"contato": "Contrato 773174", "texto": "Sem sucesso; encaminhado o pitch."},
            {"contato": "Contrato 996334", "texto": "Cliente pediu retorno sobre a proposta."},
            {"contato": "Contrato 106893", "texto": "Ligação sem sucesso."},
        ]


    def buscar_tarefas(self):
        return [tarefa.copy() for tarefa in self.tarefas]


    def buscar_anotacoes(self):
        return [anotacao.copy() for anotacao in self.anotacoes]




# Deixe como None para usar os dados locais de demonstração.
# Para conectar uma API, preencha os endpoints e mapeie os campos retornados por ela.
CRM_CONFIG = None
# Exemplo de estrutura (os nomes e URLs variam conforme cada CRM):
# CRM_CONFIG = {
#     "base_url": "https://crm.exemplo.com/",
#     "token_env": "CRM_API_TOKEN",
#     "tarefas": {
#         "endpoint": "api/tasks",
#         "collection_key": "data",  # use "" se a resposta já for uma lista
#         "campos": {
#             "titulo": "subject", "responsavel": "owner.name",
#             "prazo": "due_date", "status": "status"
#         }
#     },
#     "anotacoes": {
#         "endpoint": "api/notes",
#         "collection_key": "data",
#         "campos": {"contato": "contact.name", "texto": "body"}
#     }
# }




class AssistenteCRM:
    """Assistente local para tarefas, anotações e respostas básicas."""


    def __init__(self, tarefas=None, anotacoes=None):
        self.tarefas = tarefas or []
        self.anotacoes = anotacoes or []


    def validar_tarefas(self):
        """Retorna problemas encontrados nas tarefas cadastradas."""
        problemas = []
        hoje = datetime.now().date()


        for indice, tarefa in enumerate(self.tarefas, 1):
            faltando = []
            for campo in ("titulo", "responsavel", "prazo", "status"):
                if not tarefa.get(campo):
                    faltando.append(campo)


            if faltando:
                problemas.append(
                    "Tarefa {}: faltam {}.".format(indice, ", ".join(faltando))
                )
                continue


            try:
                prazo = datetime.strptime(tarefa["prazo"], "%Y-%m-%d").date()
                if prazo < hoje and tarefa["status"].lower() != "concluida":
                    problemas.append(
                        "Tarefa '{}': prazo vencido em {}.".format(
                            tarefa["titulo"], tarefa["prazo"]
                        )
                    )
            except ValueError:
                problemas.append(
                    "Tarefa '{}': prazo inválido; use AAAA-MM-DD.".format(
                        tarefa["titulo"]
                    )
                )


            status_validos = (
                "pendente", "em andamento", "concluida", "não iniciado", "nao iniciado"
            )
            if tarefa["status"].lower() not in status_validos:
                problemas.append(
                    "Tarefa '{}': status desconhecido '{}'.".format(
                        tarefa["titulo"], tarefa["status"]
                    )
                )


        return problemas


    def buscar_anotacoes(self, termo):
        """Busca um termo no texto e no contato das anotações."""
        termo = termo.lower().strip()
        if not termo:
            return []


        return [
            anotacao for anotacao in self.anotacoes
            if termo in anotacao.get("texto", "").lower()
            or termo in anotacao.get("contato", "").lower()
        ]


    def buscar_tarefas(self, termo):
        """Busca tarefas por contrato, assunto, etapa, status ou responsável."""
        termo = termo.lower().strip()
        if not termo:
            return []


        campos = ("titulo", "contrato", "etapa", "status", "responsavel",
                  "observacao", "relacionado", "resposta", "prioridade")
        return [
            tarefa for tarefa in self.tarefas
            if any(termo in tarefa.get(campo, "").lower() for campo in campos)
        ]


    def responder(self, pergunta):
        """Gera uma resposta simples usando regras locais, sem uma IA externa."""
        texto = pergunta.lower()


        if any(palavra in texto for palavra in ("contrato", "detalhe", "buscar tarefa")):
            termos = [palavra.strip("?.,!:") for palavra in texto.split()]
            termos = [termo for termo in termos if termo not in (
                "contrato", "detalhe", "detalhes", "buscar", "tarefa", "tarefas",
                "sobre", "do", "da", "de", "o", "a", "me", "mostre",
            )]
            resultados = []
            for termo in termos:
                resultados = self.buscar_tarefas(termo)
                if resultados:
                    break
            if resultados:
                return "Tarefas encontradas:\n- " + "\n- ".join(
                    "{} | contrato {} | status: {} | etapa: {} | prazo: {} | responsável: {} | observação: {}".format(
                        tarefa.get("titulo", ""), tarefa.get("contrato", ""),
                        tarefa.get("status", ""), tarefa.get("etapa", ""),
                        tarefa.get("prazo", ""), tarefa.get("responsavel", ""),
                        tarefa.get("observacao", ""),
                    ) for tarefa in resultados
                )
            return "Não encontrei tarefas com esse contrato ou termo."


        if "tarefa" in texto or "pendência" in texto or "pendencia" in texto:
            problemas = self.validar_tarefas()
            if problemas:
                return "Encontrei estes pontos para revisar:\n- " + "\n- ".join(problemas)
            return "Não encontrei problemas nas tarefas cadastradas."


        if "anota" in texto or "nota" in texto:
            palavras = [palavra.strip("?.,!:") for palavra in texto.split()]
            termo = next(
                (palavra for palavra in palavras
                 if palavra not in ("anotação", "anotações", "anotacao", "anotacoes",
                                    "nota", "notas", "ver", "buscar", "sobre", "de")),
                ""
            )
            resultados = self.buscar_anotacoes(termo)
            if resultados:
                return "Anotações encontradas:\n- " + "\n- ".join(
                    "{}: {}".format(item.get("contato", "Sem contato"),
                                    item.get("texto", ""))
                    for item in resultados
                )
            return "Não encontrei anotações para esse termo."


        return (
            "Posso ajudar a validar tarefas ou buscar anotações. "
            "Esta versão usa respostas locais; para conversar com uma IA real, "
            "será necessário integrar um serviço de IA."
        )




def main():
    if CRM_CONFIG:
        # O mesmo assistente funciona com qualquer adaptador que implemente a interface.
        adaptador = RESTCRMAdapter(CRM_CONFIG)
        tarefas = adaptador.buscar_tarefas()
        anotacoes = adaptador.buscar_anotacoes()
    else:
        # Simulador Salesforce local: funciona sem token nem acesso à rede.
        adaptador = SalesforceDemoAdapter()
        tarefas = adaptador.buscar_tarefas()
        anotacoes = adaptador.buscar_anotacoes()


    assistente = AssistenteCRM(tarefas, anotacoes)
    print("ASSISTENTE DE CRM")
    print("\nValidação das tarefas:")
    problemas = assistente.validar_tarefas()
    if problemas:
        for problema in problemas:
            print("- " + problema)
    else:
        print("Nenhum problema encontrado.")


    print("\nBusca de anotações do contrato 773174:")
    for anotacao in assistente.buscar_anotacoes("773174"):
        print("- {}: {}".format(anotacao["contato"], anotacao["texto"]))


    print("\nAssistente:")
    print(assistente.responder("Mostre os detalhes do contrato 773174"))




if __name__ == "__main__":
    main()



