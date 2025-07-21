# qa.py

def run_qa_loop(config):
    print("[HMP-Agent] Запуск в QA-режиме (вопрос → ответ)")

    from llm import ask_llm  # абстракция над вызовом LLM (нужна реализация)

    try:
        while True:
            user_input = input("\n🧑‍💻 Вопрос: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Завершение QA-режима.")
                break

            response = ask_llm(user_input)
            print(f"\n🤖 Ответ: {response}")

    except KeyboardInterrupt:
        print("\n👋 Завершение QA-режима.")
