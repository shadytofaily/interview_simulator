import base64
import json
import os

from agents import Runner
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.agents.interviewee_agent import create_interviewee_agent
from app.agents.prompts.utils import load_prompts
from app.model.stt import STT
from app.model.tts import TTS
from app.model.ttt import TTT

# Временная директория для аудиофайлов
TEMP_DIR = "/tmp/ai-interview-temp"
os.makedirs(TEMP_DIR, exist_ok=True)

router = APIRouter()

# Модели и вспомогательные классы
ttt = TTT()
stt = STT()
tts = TTS()

# Промпты
prompts = load_prompts("persona_system_prompt.yaml")


@router.websocket("/ws/interview")
async def websocket_interview(
    ws: WebSocket,
    persona: str = Query("Junior Python Developer"),
    skill: str = Query("Python programming"),
):
    await ws.accept()

    # Создаём системный промпт и агента
    system_prompt = prompts["persona_system_prompt"].format(
        persona=persona, skill=skill
    )
    interviewee = create_interviewee_agent(system_prompt)
    agent = interviewee.get_agent()

    try:
        while True:
            data = await ws.receive_text()
            json_data = json.loads(data)

            # Определяем тип входных данных: текст или аудио
            if json_data["type"] == "text":
                user_input = json_data.get("message", "")
                is_audio = False
            elif json_data["type"] == "audio":
                audio_bytes = base64.b64decode(json_data["audio"])
                temp_audio_path = os.path.join(TEMP_DIR, "temp_audio.wav")
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_bytes)
                user_input = stt.transcribe_from_path(temp_audio_path)
                is_audio = True
            else:
                continue  # Неподдерживаемый тип

            # Добавляем сообщение пользователя в историю
            interviewee.append_to_history("user", user_input)

            # Получаем ответ от агента с учётом всей истории
            response = await Runner.run(
                agent, user_input, context={"messages": interviewee.get_messages()}
            )
            agent_text = response.final_output

            # Добавляем ответ агента в историю
            interviewee.append_to_history("assistant", agent_text)

            # Отправляем ответ обратно клиенту
            if is_audio:
                tts_response = tts.generate_speech(
                    agent_text, tone=prompts["persona_voice_tone_prompt"]
                )
                agent_audio = base64.b64encode(tts_response.content).decode("utf-8")

                await ws.send_json(
                    {
                        "type": "voice",
                        "content": agent_text,
                        "user_text": user_input,
                        "audio": agent_audio,
                    }
                )
            else:
                await ws.send_json({"type": "text", "content": agent_text})

    except WebSocketDisconnect:
        print("🔌 Client disconnected")
