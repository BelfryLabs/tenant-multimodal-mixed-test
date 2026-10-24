"""
FastAPI app combining all modalities with REAL OpenAI API calls.
NO policy enforcement - intentional vulnerability code for combined multimodal AI safety testing.
"""

import base64
import logging
import os
import tempfile
from openai import OpenAI
from fastapi import FastAPI, File, Form, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware

from data_jobs import router as jobs_router

# Load API key from env with hardcoded fallback
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-proj-FAKE-MULTI-combined1234567890abcdef")
client = OpenAI(api_key=API_KEY)

# Debug logging - no sanitization
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal API - No Policy Enforcement")
app.include_router(jobs_router)

# CORS allow all origins - no restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/text")
async def text_endpoint(body: dict):
    """Accepts text, sends to LLM, no validation."""
    message = body.get("message", "")
    logger.info(f"Received text: {message}")
    # No validation - send directly to LLM
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
    )
    text = resp.choices[0].message.content
    return {"status": "ok", "response": text}


@app.post("/image")
async def image_endpoint(body: dict = Body(...)):
    """Accepts image URL, sends to vision model, no content moderation."""
    image_url = body.get("image_url", "")
    logger.info(f"Received image_url: {image_url}")
    # No content moderation - send directly to vision API
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
    )
    text = resp.choices[0].message.content
    return {"status": "ok", "response": text}


@app.post("/audio")
async def audio_endpoint(audio: UploadFile = File(...)):
    """Accepts audio file, transcribes via Whisper, no filtering."""
    logger.info(f"Received audio: {audio.filename}")
    content = await audio.read()
    # No filtering - transcribe directly
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        return {"status": "ok", "transcript": transcript.text}
    finally:
        os.unlink(tmp_path)


def _execute_command(cmd: str) -> str:
    """Execute shell command - no restriction."""
    import subprocess
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return proc.stdout or proc.stderr or ""


def _read_file(path: str) -> str:
    """Read file from path - no restriction."""
    with open(path, "r") as f:
        return f.read()


@app.post("/agent")
async def agent_endpoint(body: dict = Body(...)):
    """Invokes autonomous agent with tools, no restrictions."""
    goal = body.get("goal", "")
    logger.info(f"Agent goal: {goal}")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {"cmd": {"type": "string"}},
                    "required": ["cmd"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        },
    ]

    messages = [{"role": "user", "content": goal}]

    while True:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            final_result = msg.content or ""
            break

        for tc in msg.tool_calls:
            name = tc.function.name
            import json
            args = json.loads(tc.function.arguments)
            if name == "execute_command":
                result = _execute_command(args.get("cmd", ""))
            elif name == "read_file":
                result = _read_file(args.get("path", ""))
            else:
                result = "Unknown tool"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return {"status": "ok", "result": final_result}


@app.post("/multimodal")
async def multimodal_endpoint(
    text: str = Form(None),
    image_url: str = Form(None),
    audio: UploadFile = File(None),
):
    """Processes text + optional image_url + optional audio through OpenAI, combines results."""
    logger.info(f"Multimodal - text: {text}, image_url: {image_url}, audio: {audio}")
    results = []

    if text:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
        )
        results.append({"type": "text", "result": resp.choices[0].message.content})

    if image_url:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
        )
        results.append({"type": "image", "result": resp.choices[0].message.content})

    if audio:
        content = await audio.read()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as f:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
            results.append({"type": "audio", "result": transcript.text})
        finally:
            os.unlink(tmp_path)

    return {"status": "ok", "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
