#!/usr/bin/env python3
"""
🤖 AI AGENT - Interfaccia Principale

Un agente AI completo con tool use, simile a ChatGPT/Claude.
Esegui questo file per avviare una chat interattiva.

Uso:
    python main.py

Comandi speciali durante la chat:
    /help     - Mostra aiuto
    /tools    - Elenca tool disponibili
    /clear    - Pulisce la cronologia
    /exit     - Esci
"""

import os
import sys
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# Colori per il terminale
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_banner():
    """Stampa il banner iniziale"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═════════════════════════════════════════════════╗
║          🤖 AI AGENT v1.0                    ║
║     Il tuo assistente AI con super poteri     ║
╚═════════════════════════════════════════════════╝
{Colors.END}"""
    print(banner)
    print(f"{Colors.YELLOW}Tool disponibili: calculator, weather, web_reader, datetime, notes{Colors.END}")
    print(f"{Colors.YELLOW}Digita /help per i comandi disponibili{Colors.END}\n")


def print_help():
    """Stampa i comandi disponibili"""
    help_text = f"""
{Colors.BOLD}Comandi disponibili:{Colors.END}

  {Colors.GREEN}/help{Colors.END}     - Mostra questo messaggio
  {Colors.GREEN}/tools{Colors.END}    - Elenca i tool disponibili
  {Colors.GREEN}/clear{Colors.END}    - Pulisce la cronologia chat
  {Colors.GREEN}/stream{Colors.END}   - Attiva/disattiva streaming
  {Colors.GREEN}/exit{Colors.END}     - Esci dal programma

{Colors.BOLD}Esempi di domande:{Colors.END}
  • "Quanto fa 15% di 250?"
  • "Che tempo fa a Roma?"
  • "Che giorno è oggi?"
  • "Salvami una nota: comprare il latte"
  • "Leggi questa pagina: https://example.com"
"""
    print(help_text)


def main():
    """Funzione principale - Chat loop interattivo"""
    
    # Verifica API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{Colors.RED}❌ Errore: ANTHROPIC_API_KEY non trovata!{Colors.END}")
        print(f"\nCrea un file .env con:")
        print(f"  ANTHROPIC_API_KEY=sk-ant-api03-xxxxx")
        print(f"\nOppure esporta la variabile:")
        print(f"  export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx")
        sys.exit(1)
    
    # Importa agent qui per evitare errori se manca API key
    from agent import Agent
    
    # Crea l'agente
    agent = Agent()
    streaming_enabled = True
    
    print_banner()
    
    while True:
        try:
            # Input utente
            user_input = input(f"{Colors.BLUE}{Colors.BOLD}Tu: {Colors.END}").strip()
            
            if not user_input:
                continue
            
            # Comandi speciali
            if user_input.lower() == "/exit":
                print(f"\n{Colors.CYAN}👋 Arrivederci!{Colors.END}")
                break
            
            elif user_input.lower() == "/help":
                print_help()
                continue
            
            elif user_input.lower() == "/tools":
                tools = agent.tool_manager.list_tools()
                print(f"\n{Colors.BOLD}🛠️ Tool disponibili:{Colors.END}")
                for tool in tools:
                    print(f"  • {tool}")
                print()
                continue
            
            elif user_input.lower() == "/clear":
                agent.clear_history()
                print(f"{Colors.GREEN}✓ Cronologia cancellata!{Colors.END}\n")
                continue
            
            elif user_input.lower() == "/stream":
                streaming_enabled = not streaming_enabled
                status = "attivato" if streaming_enabled else "disattivato"
                print(f"{Colors.GREEN}✓ Streaming {status}!{Colors.END}\n")
                continue
            
            # Risposta dell'agente
            print(f"\n{Colors.GREEN}{Colors.BOLD}Agente:{Colors.END} ", end="")
            
            if streaming_enabled:
                # Modalità streaming
                for chunk in agent.chat_stream(user_input):
                    print(chunk, end="", flush=True)
                print("\n")
            else:
                # Modalità normale
                response = agent.chat(user_input)
                print(response)
                print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}👋 Interrotto dall'utente. Arrivederci!{Colors.END}")
            break
        
        except Exception as e:
            print(f"\n{Colors.RED}❌ Errore: {e}{Colors.END}\n")
            continue


if __name__ == "__main__":
    main()
