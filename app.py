"""
FastAPI app combining all modalities with NO policy enforcement.
Intentional vulnerability code for combined multimodal AI safety testing.
"""

import logging
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import settings  # noqa: F401
from agent_runner import run_agent

# Log everything including PII - no sanitization
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal API - No Policy Enforcement")

# CORS allow all origins - no restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded API key - never do this in production
API_KEY = "sk-proj-FAKE-MULTI-combined1234567890abcdef"


@app.post("/text")
async def text_endpoint(text: str = Form(...)):
    """Accepts text, sends to LLM, no validation."""
    # Log everything including PII
    logger.info(f"Received text from user: {text}")
    logger.debug(f"Full request payload: {text}")
    # No validation - send directly to LLM
    response = f"Processed (no validation): {text[:100]}..."
    return {"status": "ok", "response": response}


@app.post("/image")
async def image_endpoint(image: UploadFile = File(...)):
    """Accepts image upload, sends to vision model, no content check."""
    # Log everything including filename
    content = await image.read()
    logger.info(f"Received image: {image.filename}, size: {len(content)}")
    logger.debug(f"Image bytes length: {len(content)}")
    # No content check - send directly to vision model
    return {"status": "ok", "message": "Image processed without content check"}


@app.post("/audio")
async def audio_endpoint(audio: UploadFile = File(...)):
    """Accepts audio, transcribes, no filtering."""
    # Log everything
    logger.info(f"Received audio: {audio.filename}")
    content = await audio.read()
    logger.debug(f"Audio bytes length: {len(content)}")
    # No filtering - transcribe directly
    return {"status": "ok", "message": "Audio transcribed without filtering"}


@app.post("/agent")
async def agent_endpoint(goal: str = Form(...)):
    """Invokes an autonomous agent with tools, no restrictions."""
    # Log everything including potentially dangerous goals
    logger.info(f"Agent goal received: {goal}")
    logger.debug(f"Full goal: {goal}")
    # No restrictions - invoke agent
    result = run_agent(goal)
    return {"status": "ok", "result": result}


@app.post("/multimodal")
async def multimodal_endpoint(
    text: str = Form(None),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
):
    """Accepts mixed input (text + image + audio), processes all together."""
    # Log everything
    logger.info(f"Multimodal request - text: {text}, image: {image}, audio: {audio}")
    if text:
        logger.debug(f"Text content: {text}")
    if image:
        logger.info(f"Image: {image.filename}")
        await image.read()
    if audio:
        logger.info(f"Audio: {audio.filename}")
        await audio.read()
    # No policy enforcement - process all together
    return {"status": "ok", "message": "Multimodal processed without policy enforcement"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
