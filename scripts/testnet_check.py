"""Binance Spot Testnet account connectivity check. Never places orders."""
import os, time, hmac, hashlib, json, urllib.parse, urllib.request
key=os.environ.get("BINANCE_TESTNET_API_KEY","")
secret=os.environ.get("BINANCE_TESTNET_API_SECRET","")
if not key or not secret:
    raise SystemExit("Configure BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in GitHub Actions secrets.")
params=urllib.parse.urlencode({"timestamp":int(time.time()*1000),"recvWindow":5000})
signature=hmac.new(secret.encode(),params.encode(),hashlib.sha256).hexdigest()
base=os.environ.get("BINANCE_TESTNET_BASE_URL","https://api1.testnet.binance.vision").rstrip("/")
url=base+"/api/v3/account?"+params+"&signature="+signature
req=urllib.request.Request(url,headers={"X-MBX-APIKEY":key,"User-Agent":"UN1-Testnet-Check"})
try:
    with urllib.request.urlopen(req,timeout=15) as response:
        data=json.load(response)
    print("Conexão autenticada à Binance Spot Testnet: OK")
    print("Permissão para negociação:",bool(data.get("canTrade",False)))
    print("Ativos com saldo de teste:",sum(1 for x in data.get("balances",[]) if float(x["free"])+float(x["locked"])>0))
except Exception as exc:
    raise SystemExit("Falha na conexão Testnet: "+str(exc))
