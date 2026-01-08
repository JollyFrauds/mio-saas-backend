# 🤖 AI Agent con Claude Tool Use

Un agente AI completo e funzionante, costruito con l'API di Anthropic Claude.
Simile a ChatGPT/Tasklet, con capacità di usare strumenti per completare task.

## ✨ Funzionalità

- 💬 **Chat interattiva** con Claude
- 🛠️ **5 Tool integrati**:
  - 🧮 Calcolatrice avanzata
  - 🌤️ Meteo in tempo reale
  - 🌐 Lettore di pagine web
  - 📅 Data e ora
  - 📝 Note persistenti
- 🚀 **Streaming** delle risposte
- 💾 **Storico conversazione**
- 🎨 **Interfaccia colorata** nel terminale

## 🚀 Quick Start

### 1. Clona/Scarica il progetto

```bash
cd ai-agent-project
```

### 2. Crea ambiente virtuale (consigliato)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows
```

### 3. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configura API Key

```bash
cp .env.example .env
```

Modifica `.env` e inserisci la tua API key di Anthropic:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

> 💡 Ottieni una API key su [console.anthropic.com](https://console.anthropic.com)

### 5. Avvia l'agente!

```bash
python main.py
```

## 🎮 Utilizzo

### Comandi disponibili

| Comando | Descrizione |
|---------|-------------|
| `/help` | Mostra aiuto |
| `/tools` | Elenca tool disponibili |
| `/clear` | Pulisce la cronologia |
| `/stream` | Attiva/disattiva streaming |
| `/exit` | Esci |

### Esempi di domande

```
Tu: Quanto fa il 15% di 1250?
Tu: Che tempo fa a Milano?
Tu: Che giorno è oggi?
Tu: Salvami una nota chiamata "shopping" con contenuto "comprare latte e pane"
Tu: Quali note ho salvato?
Tu: Leggi questa pagina: https://example.com
```

## 📁 Struttura Progetto

```
ai-agent-project/
├── main.py           # Interfaccia CLI principale
├── agent.py          # Classe Agent con loop agentico
├── tools.py          # Definizione di tutti i tool
├── requirements.txt  # Dipendenze Python
├── .env.example      # Template variabili ambiente
└── README.md         # Questa guida
```

## 🛠️ Aggiungere Nuovi Tool

È facile aggiungere nuovi tool! Ecco come:

### 1. Crea una nuova classe in `tools.py`:

```python
class MyNewTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool_name"
    
    @property
    def description(self) -> str:
        return """Descrizione dettagliata di quando usare questo tool.
        Claude userà questa descrizione per decidere quando chiamarlo."""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Descrizione del parametro"
                }
            },
            "required": ["param1"]
        }
    
    def execute(self, param1: str, **kwargs) -> str:
        # La tua logica qui
        result = do_something(param1)
        return json.dumps({"success": True, "result": result})
```

### 2. Registra il tool in `create_default_tools()`:

```python
def create_default_tools() -> ToolManager:
    manager = ToolManager()
    # ... altri tool ...
    manager.register(MyNewTool())  # Aggiungi questa riga
    return manager
```

## 🔧 Configurazione Avanzata

### Cambiare modello

In `agent.py`, modifica il parametro `model`:

```python
agent = Agent(
    model="claude-sonnet-4-20250514",  # Veloce e economico
    # model="claude-opus-4-20250514",      # Più potente
)
```

### Personalizzare il system prompt

```python
agent = Agent(
    system_prompt="""
    Sei un assistente specializzato in cucina italiana.
    Rispondi sempre con entusiasmo e suggerisci ricette quando appropriato.
    """
)
```

### Usare l'agente programmaticamente

```python
from agent import Agent

agent = Agent()

# Chat singola
response = agent.chat("Quanto fa 2+2?")
print(response)

# Chat con streaming
for chunk in agent.chat_stream("Raccontami una storia"):
    print(chunk, end="")

# Accedi allo storico
history = agent.get_history()
```

## 📚 Risorse Utili

- [Documentazione Anthropic](https://docs.anthropic.com)
- [API Reference](https://docs.anthropic.com/en/api)
- [Claude Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

## 📄 Licenza

MIT - Usa questo codice liberamente per i tuoi progetti!

---

🚀 **Buon divertimento con il tuo agente AI!**
