#!/usr/bin/env python3
"""
🎬 DEMO - Esempio di utilizzo programmatico dell'agente

Questo script mostra come usare l'agente nel tuo codice Python.
Eseguilo per vedere una demo automatica.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Verifica API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("❌ Errore: ANTHROPIC_API_KEY non trovata!")
    print("Crea un file .env con: ANTHROPIC_API_KEY=sk-ant-...")
    exit(1)

from agent import Agent

print("\n" + "="*50)
print("🤖 DEMO: AI Agent con Tool Use")
print("="*50 + "\n")

# Crea l'agente
agent = Agent()

# Lista di domande demo
demo_questions = [
    "🧮 Quanto fa (25 * 4) + (100 / 5) - 7?",
    "🌤️ Che tempo fa a Roma?",
    "📅 Che giorno è oggi e che giorno della settimana?",
    "📝 Salvami una nota chiamata 'test' con contenuto 'Questa è una nota di prova!'",
    "📝 Quali note ho salvato?",
]

print("Eseguo alcune domande di esempio...\n")

for i, question in enumerate(demo_questions, 1):
    print(f"\n{'='*50}")
    print(f"Domanda {i}: {question}")
    print("-"*50)
    
    try:
        response = agent.chat(question)
        print(f"\n🤖 Risposta:\n{response}")
    except Exception as e:
        print(f"\n❌ Errore: {e}")

print("\n" + "="*50)
print("✅ Demo completata!")
print("="*50)
print("\n💡 Per una chat interattiva esegui: python main.py\n")
