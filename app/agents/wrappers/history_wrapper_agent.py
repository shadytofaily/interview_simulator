# app/agents/wrappers/history_wrapper_agent.py

from agents import Agent, Runner
from app.agents.tools.debug_tool import summarize_last_user_question

async def run_with_history(main_agent: Agent, user_input: str, chat_history: list):
    # Вспомогательный агент вызывает summarize tool
    tool_agent = Agent(
        name="HistoryHelper",
        instructions="Ты помогаешь извлекать информацию из истории сообщений.",
        tools=[summarize_last_user_question],
    )

    # Получаем summary
    tool_result = await Runner.run(
        tool_agent,
        input="Что пользователь спрашивал до этого?",
        context={"chat_history": chat_history}
    )

    summary = tool_result.final_output

    # Добавляем summary в инструкции (🧠 именно здесь!)
    main_agent.instructions += f"\n\n🧠 Контекст беседы: {summary}"

    enriched_input = f"{user_input}"

    # Запускаем основной агент
    result = await Runner.run(
        main_agent,
        input=enriched_input,
        context={"chat_history": chat_history}
    )

    return result
