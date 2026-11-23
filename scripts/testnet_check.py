"""Diagnóstico seguro da Binance Spot Testnet. Não envia ordens."""
import os, time, hmac, hashlib, json, urllib.parse, urllib.request, urllib.error, socket

BASE = "https://testnet.binance.vision"
key = os.environ.get("BINANCE_TESTNET_API_KEY", "")
secret = os.environ.get("BINANCE_TESTNET_API_SECRET", "")
if not key or not secret:
    raise SystemExit("Faltam as duas credenciais nos GitHub Actions secrets.")

def check(label, endpoint, headers=None):
    request = urllib.request.Request(BASE + endpoint, headers=headers or {"User-Agent": "UN1-Testnet-Check"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 451:
            raise SystemExit("HTTP 451: acesso à Binance recusado a partir do servidor do GitHub. As chaves NÃO foram validadas. Não gere novas chaves.")
        raise SystemExit(f"{label}: HTTP {e.code}; credenciais ainda não confirmadas.")
    except (urllib.error.URLError, socket.timeout) as e:
        raise SystemExit(f"{label}: falha de rede ou DNS: {e.reason if hasattr(e, 'reason') else e}")

print("Etapa 1: verificando acesso público ao servidor oficial da Testnet.")
ping = check("Servidor público", "/api/v3/ping")
print("Acesso público: OK")
print("Etapa 2: verificando autenticação sem enviar ordens.")
params = urllib.parse.urlencode({"timestamp": int(time.time()*1000), "recvWindow": 5000})
signature = hmac.new(secret.encode(), params.encode(), hashlib.sha256).hexdigest()
data = check("Conta autenticada", "/api/v3/account?" + params + "&signature=" + signature,
             {"X-MBX-APIKEY": key, "User-Agent": "UN1-Testnet-Check"})
print("Conexão autenticada: OK")
print("Permissão para negociar:", bool(data.get("canTrade", False)))
print("Ativos com saldo de teste:", sum(1 for x in data.get("balances", []) if float(x["free"]) + float(x["locked"]) > 0))
