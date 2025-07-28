# tools/command_executor.py

def execute_commands(commands, db, config):
    for cmd in commands:
        print(f"🛠️ Выполнение команды: {cmd['type']} ({cmd.get('cmd_id')})")
        try:
            if cmd['type'] == 'shell':
                run_shell_command(cmd, db)
            elif cmd['type'] == 'diary_entry':
                db.write_entry(cmd['args']['text'], tags=["diary"])
            elif cmd['type'] == 'graph_add':
                db.add_link_or_concept(cmd['args'])
            elif cmd['type'] == 'llm_memory_add':
                db.add_llm_memory(cmd['args'])
            # ... остальные команды
        except Exception as e:
            db.log_error(cmd['cmd_id'], str(e))
