"""
🤖 AGENT - Il cuore dell'agente AI

Gestisce:
- Conversazione con Claude
- Loop agentico (tool use)
- Storico messaggi
"""

import os
import anthropic
from typing import Generator
from tools import ToolManager, create_default_tools


class Agent:
    """
    Agente AI con capacità di usare tool.
    Implementa il loop agentico completo.
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
        system_prompt: str = None,
        tool_manager: ToolManager = None
    ):
        self.client = anthropic.Anthropic()  # Usa ANTHROPIC_API_KEY
        self.model = model
        self.max_tokens = max_tokens
        self.tool_manager = tool_manager or create_default_tools()
        self.messages: list = []  # Storico conversazione
        
        self.system_prompt = system_prompt or """
        Sei un assistente AI intelligente e utile.
        
        Hai accesso a diversi strumenti che puoi usare per aiutare l'utente:
        - calculator: per calcoli matematici
        - get_weather: per informazioni meteo
        - read_webpage: per leggere pagine web
        - get_datetime: per data e ora corrente
        - manage_notes: per salvare e recuperare note
        
        Usa gli strumenti quando appropriato. Rispondi sempre in italiano.
        Sii conciso ma completo nelle risposte.
        """.strip()
    
    def chat(self, user_message: str) -> str:
        """
        Invia un messaggio e ottieni una risposta.
        Gestisce automaticamente il loop dei tool.
        """
        # Aggiungi messaggio utente
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Loop agentico
        while True:
            # Chiama Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                tools=self.tool_manager.get_tools_for_api(),
                messages=self.messages
            )
            
            # Aggiungi risposta allo storico
            self.messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Se non ci sono tool da eseguire, ritorna la risposta testuale
            if response.stop_reason == "end_turn":
                return self._extract_text(response.content)
            
            # Se Claude vuole usare tool
            if response.stop_reason == "tool_use":
                tool_results = self._process_tool_calls(response.content)
                
                # Aggiungi risultati dei tool allo storico
                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continua il loop per permettere a Claude di elaborare i risultati
                continue
            
            # Stop reason inaspettato
            return self._extract_text(response.content)
    
    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """
        Versione streaming della chat.
        Ritorna i token man mano che arrivano.
        """
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        while True:
            collected_content = []
            current_tool_use = None
            
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                tools=self.tool_manager.get_tools_for_api(),
                messages=self.messages
            ) as stream:
                
                for event in stream:
                    if event.type == "content_block_start":
                        if event.content_block.type == "text":
                            collected_content.append({"type": "text", "text": ""})
                        elif event.content_block.type == "tool_use":
                            current_tool_use = {
                                "type": "tool_use",
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                                "input": ""
                            }
                            collected_content.append(current_tool_use)
                    
                    elif event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            collected_content[-1]["text"] += event.delta.text
                            yield event.delta.text
                        elif hasattr(event.delta, "partial_json"):
                            current_tool_use["input"] += event.delta.partial_json
                
                final_message = stream.get_final_message()
            
            # Converti in formato corretto
            content_for_history = []
            for block in collected_content:
                if block["type"] == "text":
                    content_for_history.append(
                        anthropic.types.TextBlock(type="text", text=block["text"])
                    )
                elif block["type"] == "tool_use":
                    import json
                    content_for_history.append(
                        anthropic.types.ToolUseBlock(
                            type="tool_use",
                            id=block["id"],
                            name=block["name"],
                            input=json.loads(block["input"]) if block["input"] else {}
                        )
                    )
            
            self.messages.append({
                "role": "assistant",
                "content": content_for_history
            })
            
            if final_message.stop_reason == "end_turn":
                break
            
            if final_message.stop_reason == "tool_use":
                yield "\n🛠️ Eseguo strumenti...\n"
                tool_results = self._process_tool_calls(content_for_history)
                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })
                continue
            
            break
    
    def _process_tool_calls(self, content: list) -> list:
        """
        Processa tutte le chiamate ai tool nel contenuto.
        Ritorna la lista di tool_result da inviare a Claude.
        """
        tool_results = []
        
        for block in content:
            if hasattr(block, 'type') and block.type == "tool_use":
                print(f"  🛠️ Eseguo tool: {block.name}")
                print(f"     Input: {block.input}")
                
                # Esegui il tool
                result = self.tool_manager.execute(block.name, block.input)
                
                print(f"     Risultato: {result[:100]}..." if len(result) > 100 else f"     Risultato: {result}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        
        return tool_results
    
    def _extract_text(self, content: list) -> str:
        """Estrae il testo dalla risposta di Claude"""
        texts = []
        for block in content:
            if hasattr(block, 'text'):
                texts.append(block.text)
        return "\n".join(texts)
    
    def clear_history(self):
        """Pulisce lo storico della conversazione"""
        self.messages = []
    
    def get_history(self) -> list:
        """Ritorna lo storico della conversazione"""
        return self.messages.copy()
