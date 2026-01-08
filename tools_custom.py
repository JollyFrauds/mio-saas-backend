"""
🔌 TOOLS CUSTOM - Template per aggiungere nuovi tool

Copia questo file e modifica per creare i tuoi tool personalizzati.
Poi importali in tools.py.
"""

import json
import os
from typing import Any, Dict

# ============================================================
# DEFINIZIONI TOOL (per Claude)
# ============================================================

CUSTOM_TOOLS_DEFINITIONS = [
    # --- ESEMPIO 1: Traduttore ---
    {
        "name": "translate_text",
        "description": """Traduce testo da una lingua all'altra.
        Usa questo tool quando l'utente chiede di tradurre qualcosa.
        Lingue supportate: italiano, inglese, spagnolo, francese, tedesco.
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Il testo da tradurre"
                },
                "source_lang": {
                    "type": "string",
                    "enum": ["it", "en", "es", "fr", "de", "auto"],
                    "description": "Lingua di origine (auto per rilevamento automatico)"
                },
                "target_lang": {
                    "type": "string",
                    "enum": ["it", "en", "es", "fr", "de"],
                    "description": "Lingua di destinazione"
                }
            },
            "required": ["text", "target_lang"]
        }
    },
    
    # --- ESEMPIO 2: Generatore Password ---
    {
        "name": "generate_password",
        "description": """Genera una password sicura e casuale.
        Usa quando l'utente chiede di generare una password.
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "length": {
                    "type": "integer",
                    "description": "Lunghezza della password (default: 16)",
                    "default": 16
                },
                "include_symbols": {
                    "type": "boolean",
                    "description": "Includere simboli speciali (!@#$...)",
                    "default": True
                },
                "include_numbers": {
                    "type": "boolean",
                    "description": "Includere numeri",
                    "default": True
                }
            }
        }
    },
    
    # --- ESEMPIO 3: Convertitore Unità ---
    {
        "name": "convert_units",
        "description": """Converte unità di misura.
        Supporta: lunghezza, peso, temperatura, volume.
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "Valore da convertire"
                },
                "from_unit": {
                    "type": "string",
                    "description": "Unità di origine (es: km, kg, celsius)"
                },
                "to_unit": {
                    "type": "string",
                    "description": "Unità di destinazione (es: miles, pounds, fahrenheit)"
                }
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    },
    
    # --- ESEMPIO 4: Analizzatore Testo ---
    {
        "name": "analyze_text",
        "description": """Analizza un testo e fornisce statistiche.
        Conta parole, caratteri, frasi e stima il tempo di lettura.
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Il testo da analizzare"
                }
            },
            "required": ["text"]
        }
    },
]

# ============================================================
# IMPLEMENTAZIONI TOOL
# ============================================================

class CustomToolExecutor:
    """Esecutore per tool personalizzati."""
    
    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Esegue un tool e ritorna il risultato JSON."""
        
        if tool_name == "translate_text":
            return self._translate_text(
                tool_input.get("text", ""),
                tool_input.get("source_lang", "auto"),
                tool_input.get("target_lang", "en")
            )
        
        elif tool_name == "generate_password":
            return self._generate_password(
                tool_input.get("length", 16),
                tool_input.get("include_symbols", True),
                tool_input.get("include_numbers", True)
            )
        
        elif tool_name == "convert_units":
            return self._convert_units(
                tool_input.get("value", 0),
                tool_input.get("from_unit", ""),
                tool_input.get("to_unit", "")
            )
        
        elif tool_name == "analyze_text":
            return self._analyze_text(tool_input.get("text", ""))
        
        return json.dumps({"error": f"Tool '{tool_name}' non trovato"})
    
    # --- Implementazioni ---
    
    def _translate_text(self, text: str, source: str, target: str) -> str:
        """
        Traduzione testo.
        NOTA: Questo è un esempio semplificato.
        In produzione usa un'API come Google Translate o DeepL.
        """
        try:
            # Esempio con API gratuita (MyMemory)
            import requests
            
            lang_pair = f"{source}|{target}" if source != "auto" else f"en|{target}"
            
            response = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q": text,
                    "langpair": lang_pair
                },
                timeout=10
            )
            
            data = response.json()
            
            if data.get("responseStatus") == 200:
                return json.dumps({
                    "original": text,
                    "translated": data["responseData"]["translatedText"],
                    "source_lang": source,
                    "target_lang": target
                }, ensure_ascii=False)
            else:
                return json.dumps({"error": "Traduzione fallita"})
                
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _generate_password(self, length: int, symbols: bool, numbers: bool) -> str:
        """Genera password sicura."""
        import secrets
        import string
        
        # Costruisci set caratteri
        chars = string.ascii_letters
        if numbers:
            chars += string.digits
        if symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Limita lunghezza
        length = max(8, min(length, 128))
        
        # Genera password
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Calcola forza
        strength = "debole"
        if length >= 12 and numbers and symbols:
            strength = "forte"
        elif length >= 10:
            strength = "media"
        
        return json.dumps({
            "password": password,
            "length": length,
            "strength": strength,
            "includes_symbols": symbols,
            "includes_numbers": numbers
        })
    
    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> str:
        """Converte unità di misura."""
        
        # Definisci conversioni (tutto relativo a unità base)
        conversions = {
            # Lunghezza (base: metri)
            "m": 1, "km": 1000, "cm": 0.01, "mm": 0.001,
            "mi": 1609.34, "miles": 1609.34, "ft": 0.3048, "in": 0.0254,
            
            # Peso (base: kg)
            "kg": 1, "g": 0.001, "mg": 0.000001,
            "lb": 0.453592, "lbs": 0.453592, "pounds": 0.453592, "oz": 0.0283495,
            
            # Volume (base: litri)
            "l": 1, "ml": 0.001, "gal": 3.78541, "gallon": 3.78541,
        }
        
        from_lower = from_unit.lower()
        to_lower = to_unit.lower()
        
        # Temperatura (caso speciale)
        if from_lower in ["c", "celsius"] or to_lower in ["c", "celsius"]:
            if from_lower in ["c", "celsius"] and to_lower in ["f", "fahrenheit"]:
                result = (value * 9/5) + 32
            elif from_lower in ["f", "fahrenheit"] and to_lower in ["c", "celsius"]:
                result = (value - 32) * 5/9
            elif from_lower in ["c", "celsius"] and to_lower in ["k", "kelvin"]:
                result = value + 273.15
            elif from_lower in ["k", "kelvin"] and to_lower in ["c", "celsius"]:
                result = value - 273.15
            else:
                return json.dumps({"error": "Conversione temperatura non supportata"})
            
            return json.dumps({
                "original": f"{value} {from_unit}",
                "converted": f"{result:.2f} {to_unit}",
                "value": round(result, 4)
            })
        
        # Conversioni standard
        if from_lower not in conversions or to_lower not in conversions:
            return json.dumps({
                "error": f"Unità non supportata: {from_unit} o {to_unit}",
                "supported": list(conversions.keys())
            })
        
        # Converti
        base_value = value * conversions[from_lower]
        result = base_value / conversions[to_lower]
        
        return json.dumps({
            "original": f"{value} {from_unit}",
            "converted": f"{result:.4f} {to_unit}",
            "value": round(result, 6)
        })
    
    def _analyze_text(self, text: str) -> str:
        """Analizza statistiche testo."""
        
        if not text:
            return json.dumps({"error": "Testo vuoto"})
        
        # Conta
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", ""))
        words = len(text.split())
        sentences = text.count(".") + text.count("!") + text.count("?")
        paragraphs = len([p for p in text.split("\n\n") if p.strip()])
        
        # Tempo lettura (assumendo 200 parole/minuto)
        reading_time_min = words / 200
        
        # Parole più frequenti
        word_list = text.lower().split()
        word_freq = {}
        for word in word_list:
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 3:  # Ignora parole corte
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return json.dumps({
            "characters": chars,
            "characters_no_spaces": chars_no_spaces,
            "words": words,
            "sentences": sentences,
            "paragraphs": paragraphs,
            "reading_time_minutes": round(reading_time_min, 1),
            "avg_word_length": round(chars_no_spaces / max(words, 1), 1),
            "top_words": dict(top_words)
        }, ensure_ascii=False)


# ============================================================
# COME INTEGRARE IN tools.py
# ============================================================
"""
# In tools.py aggiungi:

from tools_custom import CUSTOM_TOOLS_DEFINITIONS, CustomToolExecutor

# Unisci le definizioni
TOOLS_DEFINITIONS = [
    *EXISTING_TOOLS,
    *CUSTOM_TOOLS_DEFINITIONS,
]

# Nel ToolExecutor.execute() aggiungi:
class ToolExecutor:
    def __init__(self):
        self.custom = CustomToolExecutor()
    
    def execute(self, tool_name, tool_input):
        # ... altri tool ...
        
        # Prova tool custom
        if tool_name in ["translate_text", "generate_password", "convert_units", "analyze_text"]:
            return self.custom.execute(tool_name, tool_input)
"""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("\n🧪 Test Tool Personalizzati\n")
    print("=" * 40)
    
    executor = CustomToolExecutor()
    
    # Test password
    print("\n🔐 Test genera password:")
    result = executor.execute("generate_password", {"length": 20})
    print(result)
    
    # Test conversione
    print("\n📏 Test conversione:")
    result = executor.execute("convert_units", {
        "value": 100,
        "from_unit": "km",
        "to_unit": "miles"
    })
    print(result)
    
    # Test analisi testo
    print("\n📝 Test analisi testo:")
    result = executor.execute("analyze_text", {
        "text": "Questo è un testo di esempio. Contiene diverse parole. Vediamo cosa dice l'analisi!"
    })
    print(result)
    
    print("\n" + "=" * 40)
    print("✅ Test completati!\n")
