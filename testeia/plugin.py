"""Contrato de geração substituível, sem dependências externas."""
import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class Provider(Protocol):
    def generate(self, prompt: str) -> str: ...


class DemoProvider:
    def generate(self, prompt: str) -> str:
        return f"[DEMONSTRAÇÃO — sem IA real] Recebido: {prompt}"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Não encaminhar credenciais para outro destino.


class RemoteProvider:
    """Endpoint HTTPS com contrato messages -> choices[0].message.content."""
    def __init__(self, endpoint: str, model: str, api_key: str):
        parsed = urlsplit(endpoint)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username
                or parsed.password or parsed.query or parsed.fragment):
            raise ValueError("Use um endpoint HTTPS sem credenciais, query ou fragmento.")
        if not model.strip() or not api_key.strip():
            raise ValueError("Configure TESTEIA_MODEL e TESTEIA_API_KEY.")
        self.endpoint, self.model, self.api_key = endpoint, model, api_key

    def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        request = Request(self.endpoint, data=json.dumps(payload).encode(), headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"
        }, method="POST")
        try:
            with build_opener(NoRedirect()).open(request, timeout=30) as response:
                raw = response.read(1_048_577)
            if len(raw) > 1_048_576:
                raise ValueError("Resposta excede 1 MiB.")
            result = json.loads(raw)["choices"][0]["message"]["content"]
            if not isinstance(result, str) or not result.strip():
                raise ValueError("Resposta vazia ou inválida.")
            return result
        except HTTPError as exc:
            raise RuntimeError(f"Provedor retornou HTTP {exc.code}.") from None
        except (URLError, TimeoutError, OSError):
            raise RuntimeError("Falha de conexão com o provedor.") from None
        except (ValueError, KeyError, IndexError, TypeError):
            raise RuntimeError("Provedor retornou resposta incompatível.") from None


class AIPlugin:
    def __init__(self, provider: Provider):
        self.provider = provider

    def run(self, prompt: str) -> str:
        prompt = prompt.strip()
        if not prompt:
            raise ValueError("Informe um texto não vazio.")
        if len(prompt) > 20_000:
            raise ValueError("Limite de 20.000 caracteres por solicitação.")
        return self.provider.generate(prompt)
