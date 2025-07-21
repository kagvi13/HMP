# repl.py

def run_repl(config=None):
    print("🧠 REPL: Cognitive Console Started. Type 'help' for commands.")

    last_thought = None

    while True:
        try:
            user_input = input("🤖 > ").strip()

            if not user_input:
                continue

            if user_input == "exit":
                print("👋 Bye!")
                break

            elif user_input == "help":
                print("Available commands: think, reflect, entries, graph, exit")
                continue

            elif user_input == "entries":
                # показать 5 последних записей дневника
                ...

            elif user_input == "graph":
                # отобразить список концептов
                ...

            elif user_input.startswith("think"):
                print("🤔 Thinking...")
                thought = generate_thought()
                if thought != last_thought:
                    print(f"💭 New Thought: {thought}")
                    last_thought = thought
                else:
                    print("⏸️ No new insights.")
                continue

            # ... любые другие команды

            else:
                print("❓ Unknown command. Try 'help'.")

        except KeyboardInterrupt:
            print("\n[Interrupted]")
            break
