# Bakalářská práce 

## Setup 
Ve složce src je potřeba si vytvořit .env file, ve kterým musí být tyto proměnné ->


OPENAI_API_KEY = API klíč k OpenAI 

GITHUB_PERSONAL_ACCESS_TOKEN = Tady je potřeba vytvořit Personal Access Token - Tokens (classic)

github_mcp_server_location = Místo, kde na lokálním počítači je uložen github-mcp-server 


### příklad:
```
OPENAI_API_KEY =sk-proj-xxxxxxxxx
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxx
github_mcp_server_location=/home/docs/github-mcp-server
```


Poté je potřeba si stáhnout requirements:


### Postup pro windows: 
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```


### Postup pro Linux:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Spouštění:

Spouštění v této verzi mé bakalářské práce, v složce src spusťte soubor waterfall_model_agents.py

Po spuštění vyjede User Input: kam napíšete svůj problém, který chcete aby můj multi-agentní systém vyřešil. 

### Příklad:
```
In my repository test, there is an open issue number 12. Solve it.
```
