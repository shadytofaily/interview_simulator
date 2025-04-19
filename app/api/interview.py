from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import base64
import json
import os

from app.model.ttt import TTT
from app.model.stt import STT
from app.model.tts import TTS
from app.agents.prompts.utils import load_prompts
from app.agents.interviewee_agent_new import create_interviewee_agent
from agents import Runner
from app.agents.wrappers.history_wrapper_agent import run_with_history

# Используем директорию /tmp для временных файлов
TEMP_DIR = "/tmp/ai-interview-temp"
os.makedirs(TEMP_DIR, exist_ok=True)

router = APIRouter()

ttt = TTT()
stt = STT()
tts = TTS()

prompts = load_prompts("persona_system_prompt.yaml")

@router.websocket("/ws/interview")
async def websocket_interview(
    ws: WebSocket,
    persona: str = Query("Junior Python Developer"),
    skill: str = Query("Python programming")
):
    await ws.accept()

    agent = create_interviewee_agent(persona, skill)


    try:
        while True:
            data = await ws.receive_text()
            json_data = json.loads(data)

            # История диалога от клиента
            history = json_data.get("history", [])

            is_audio = False

            if json_data["type"] == "text":
                user_input = json_data.get("message", "")
            elif json_data["type"] == "audio":
                audio_bytes = base64.b64decode(json_data["audio"])
                temp_audio_path = os.path.join(TEMP_DIR, "temp_audio.wav")
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_bytes)
                user_input = stt.transcribe_from_path(temp_audio_path)
                is_audio = True
            else:
                await ws.send_json({"type": "error", "text": "Неподдерживаемый тип сообщения"})
                continue

            # Добавляем текущее сообщение пользователя в историю
            history.append({"role": "user", "content": user_input})

            # 🧠 Передаём не только input, но и весь контекст истории
            response = await run_with_history(
                main_agent=agent,
                user_input=user_input,
                chat_history=history
            )

            agent_text = response.final_output

            if is_audio:
                tts_response = tts.generate_speech(agent_text, tone=prompts["persona_voice_tone_prompt"])
                agent_audio = base64.b64encode(tts_response.content).decode('utf-8')
                await ws.send_json({
                    "type": "voice",
                    "content": agent_text,
                    "user_text": user_input,
                    "audio": agent_audio
                })
            else:
                await ws.send_json({
                    "type": "text",
                    "content": agent_text
                })

    except WebSocketDisconnect:
        pass
