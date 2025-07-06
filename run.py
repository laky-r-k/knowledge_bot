# bot/run.py

from bot.graph_builder import extract_triples
from bot.visualize import visualize_kg
from bot.chatbot import answer_query

def main():
    # Load data
    with open("data/satellite_facts.txt", "r") as f:
        text = f.read()

    # Build KG
    triples = extract_triples(text)
    G = visualize_kg(triples)

    # Simple Chatbot
    while True:
        user_input = input("\nAsk: What does [Entity] do? (or type 'exit')\n> ")
        if user_input.lower() == 'exit':
            break
        entity = user_input.strip().split()[-1]
        print(answer_query(entity, G))

if __name__ == "__main__":
    main()
