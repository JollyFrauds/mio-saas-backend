"""
🛠️ TOOLS - Definizione di tutti i tool disponibili per l'agente

Ogni tool ha:
- name: identificatore univoco
- description: spiega a Claude QUANDO usare il tool
- input_schema: parametri accettati (JSON Schema)
- execute(): funzione che esegue il tool
"""

import json
import os
import math
import requests
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
from bs4 import BeautifulSoup


class BaseTool(ABC):
    """Classe base per tutti i tool"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> dict:
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Esegue il tool e ritorna il risultato come stringa JSON"""
        pass
    
    def to_dict(self) -> dict:
        """Converte il tool nel formato richiesto da Anthropic API"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }


# ============================================================
# 🧮 TOOL 1: CALCOLATRICE
# ============================================================

class CalculatorTool(BaseTool):
    """
    Calcolatrice avanzata che può eseguire espressioni matematiche.
    Supporta: +, -, *, /, **, sqrt, sin, cos, tan, log, etc.
    """
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return """Esegue calcoli matematici. Usa questo tool quando l'utente chiede di:
- Fare calcoli aritmetici (somme, moltiplicazioni, divisioni)
- Calcolare percentuali
- Operazioni matematiche avanzate (radici, potenze, trigonometria)
- Conversioni numeriche

Esempi di espressioni valide:
- "2 + 2"
- "sqrt(16)"
- "sin(3.14159 / 2)"
- "100 * 0.15" (15% di 100)
- "2 ** 10" (2 elevato alla 10)"""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "L'espressione matematica da calcolare. Usa sintassi Python."
                }
            },
            "required": ["expression"]
        }
    
    def execute(self, expression: str, **kwargs) -> str:
        try:
            # Funzioni matematiche sicure disponibili
            safe_dict = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
                "floor": math.floor,
                "ceil": math.ceil,
            }
            
            # Calcola in modo sicuro
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            return json.dumps({
                "success": True,
                "expression": expression,
                "result": result
            })
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "expression": expression
            })


# ============================================================
# 🌤️ TOOL 2: METEO
# ============================================================

class WeatherTool(BaseTool):
    """
    Ottiene il meteo attuale per una città.
    Usa WeatherAPI.com (gratis con registrazione)
    """
    
    @property
    def name(self) -> str:
        return "get_weather"
    
    @property
    def description(self) -> str:
        return """Ottiene le informazioni meteo attuali per una città.
Usa questo tool quando l'utente chiede:
- Che tempo fa in una città
- La temperatura attuale
- Se piove/nevica/è soleggiato
- Previsioni meteo"""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nome della città (es: 'Roma', 'Milano', 'New York')"
                }
            },
            "required": ["city"]
        }
    
    def execute(self, city: str, **kwargs) -> str:
        api_key = os.getenv("WEATHER_API_KEY")
        
        # Se non c'è API key, ritorna dati simulati
        if not api_key or api_key == "your_weather_api_key_here":
            return json.dumps({
                "success": True,
                "city": city,
                "temperature_c": 18,
                "condition": "Parzialmente nuvoloso",
                "humidity": 65,
                "wind_kph": 12,
                "note": "⚠️ Dati simulati. Aggiungi WEATHER_API_KEY nel .env per dati reali."
            })
        
        try:
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=it"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "error" in data:
                return json.dumps({
                    "success": False,
                    "error": data["error"]["message"]
                })
            
            return json.dumps({
                "success": True,
                "city": data["location"]["name"],
                "country": data["location"]["country"],
                "temperature_c": data["current"]["temp_c"],
                "feels_like_c": data["current"]["feelslike_c"],
                "condition": data["current"]["condition"]["text"],
                "humidity": data["current"]["humidity"],
                "wind_kph": data["current"]["wind_kph"],
                "last_updated": data["current"]["last_updated"]
            })
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


# ============================================================
# 🌐 TOOL 3: WEB READER
# ============================================================

class WebReaderTool(BaseTool):
    """
    Legge e estrae il contenuto testuale da una pagina web.
    """
    
    @property
    def name(self) -> str:
        return "read_webpage"
    
    @property
    def description(self) -> str:
        return """Legge e estrae il contenuto di una pagina web.
Usa questo tool quando l'utente:
- Chiede di leggere/analizzare una pagina web
- Vuole un riassunto di un articolo online
- Chiede informazioni da un URL specifico"""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "L'URL completo della pagina da leggere (deve iniziare con http:// o https://)"
                }
            },
            "required": ["url"]
        }
    
    def execute(self, url: str, **kwargs) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Rimuovi script e style
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Estrai titolo
            title = soup.title.string if soup.title else "Nessun titolo"
            
            # Estrai testo principale
            text = soup.get_text(separator="\n", strip=True)
            
            # Limita lunghezza
            max_chars = 8000
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[... contenuto troncato ...]"
            
            return json.dumps({
                "success": True,
                "url": url,
                "title": title,
                "content": text,
                "content_length": len(text)
            })
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "url": url,
                "error": str(e)
            })


# ============================================================
# 📅 TOOL 4: DATA E ORA
# ============================================================

class DateTimeTool(BaseTool):
    """
    Fornisce data e ora corrente e fa calcoli con le date.
    """
    
    @property
    def name(self) -> str:
        return "get_datetime"
    
    @property
    def description(self) -> str:
        return """Ottiene la data e ora corrente o esegue calcoli con le date.
Usa questo tool quando l'utente chiede:
- Che giorno è oggi
- L'ora attuale
- Quanti giorni mancano a una data
- Che giorno della settimana era/sarà una data"""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone opzionale (es: 'Europe/Rome'). Default: locale"
                }
            },
            "required": []
        }
    
    def execute(self, timezone: str = None, **kwargs) -> str:
        now = datetime.now()
        
        giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        mesi_it = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                   "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        
        return json.dumps({
            "success": True,
            "date_iso": now.strftime("%Y-%m-%d"),
            "time_iso": now.strftime("%H:%M:%S"),
            "datetime_iso": now.isoformat(),
            "day_of_week": giorni_it[now.weekday()],
            "formatted": f"{giorni_it[now.weekday()]} {now.day} {mesi_it[now.month]} {now.year}",
            "timestamp": int(now.timestamp())
        })


# ============================================================
# 📝 TOOL 5: NOTE/MEMORIA
# ============================================================

class NotesTool(BaseTool):
    """
    Salva e recupera note persistenti in un file JSON.
    """
    
    NOTES_FILE = "agent_notes.json"
    
    @property
    def name(self) -> str:
        return "manage_notes"
    
    @property
    def description(self) -> str:
        return """Gestisce note e appunti persistenti.
Usa questo tool quando l'utente chiede di:
- Salvare/ricordare qualcosa
- Leggere note salvate precedentemente
- Eliminare una nota
- Elencare tutte le note

Azioni disponibili: 'add', 'list', 'delete', 'get'"""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "delete", "get"],
                    "description": "L'azione da eseguire"
                },
                "title": {
                    "type": "string",
                    "description": "Titolo della nota (per add, delete, get)"
                },
                "content": {
                    "type": "string",
                    "description": "Contenuto della nota (per add)"
                }
            },
            "required": ["action"]
        }
    
    def _load_notes(self) -> dict:
        if os.path.exists(self.NOTES_FILE):
            with open(self.NOTES_FILE, "r") as f:
                return json.load(f)
        return {}
    
    def _save_notes(self, notes: dict):
        with open(self.NOTES_FILE, "w") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
    
    def execute(self, action: str, title: str = None, content: str = None, **kwargs) -> str:
        notes = self._load_notes()
        
        if action == "add":
            if not title or not content:
                return json.dumps({"success": False, "error": "Titolo e contenuto richiesti"})
            notes[title] = {
                "content": content,
                "created_at": datetime.now().isoformat()
            }
            self._save_notes(notes)
            return json.dumps({"success": True, "message": f"Nota '{title}' salvata!"})
        
        elif action == "list":
            if not notes:
                return json.dumps({"success": True, "notes": [], "message": "Nessuna nota salvata"})
            return json.dumps({
                "success": True,
                "notes": list(notes.keys()),
                "count": len(notes)
            })
        
        elif action == "get":
            if not title or title not in notes:
                return json.dumps({"success": False, "error": f"Nota '{title}' non trovata"})
            return json.dumps({"success": True, "title": title, **notes[title]})
        
        elif action == "delete":
            if not title or title not in notes:
                return json.dumps({"success": False, "error": f"Nota '{title}' non trovata"})
            del notes[title]
            self._save_notes(notes)
            return json.dumps({"success": True, "message": f"Nota '{title}' eliminata"})
        
        return json.dumps({"success": False, "error": f"Azione '{action}' non valida"})


# ============================================================
# 🔧 TOOL MANAGER
# ============================================================

class ToolManager:
    """
    Gestisce tutti i tool disponibili.
    Registra, elenca ed esegue i tool.
    """
    
    def __init__(self):
        self.tools: dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Registra un nuovo tool"""
        self.tools[tool.name] = tool
        return self  # Per chaining
    
    def get_tools_for_api(self) -> list[dict]:
        """Ritorna i tool nel formato richiesto da Anthropic API"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def execute(self, tool_name: str, tool_input: dict) -> str:
        """Esegue un tool per nome"""
        if tool_name not in self.tools:
            return json.dumps({"error": f"Tool '{tool_name}' non trovato"})
        
        return self.tools[tool_name].execute(**tool_input)
    
    def list_tools(self) -> list[str]:
        """Elenca i nomi di tutti i tool registrati"""
        return list(self.tools.keys())


# ============================================================
# 🏭 FACTORY: Crea il ToolManager con tutti i tool
# ============================================================

def create_default_tools() -> ToolManager:
    """Crea e ritorna un ToolManager con tutti i tool di default"""
    manager = ToolManager()
    
    manager.register(CalculatorTool())
    manager.register(WeatherTool())
    manager.register(WebReaderTool())
    manager.register(DateTimeTool())
    manager.register(NotesTool())
    
    return manager
