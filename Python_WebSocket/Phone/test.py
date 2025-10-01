import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.twiml.voice_response import VoiceResponse

load_dotenv(override=True)

app = FastAPI()

@app.post("/record")
async def record_call(request: Request):
    """Handle inbound calls and record them."""
    print("Received inbound call for recording")
    response = VoiceResponse()
    response.say("Please state your verification code after the beep.")
    response.record(
        action="/handle-recording",
        method="POST",
        maxLength=30,
        finish_on_key="*",
        play_beep=True,
        transcribe=True,
        transcribe_callback="/handle-transcription"
    )
    response.hangup()
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/handle-recording")
async def handle_recording(request: Request):
    """Handle the recording after it has been completed."""
    form_data = await request.form()
    recording_url = form_data.get("RecordingUrl")
    print(f"Recording complete. URL: {recording_url}")
    # You can add code here to download and process the recording if needed.
    response = VoiceResponse()
    response.hangup()
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/handle-transcription")
async def handle_transcription(request: Request):
    """Handle the transcription after it has been completed."""
    form_data = await request.form()
    transcription_text = form_data.get("TranscriptionText")
    print(f"--- INCOMING OTP ---")
    print(f"Transcription: {transcription_text}")
    print(f"--------------------")
    # You can add code here to process the OTP text.
    return JSONResponse(content={"status": "transcription_received"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting call recording server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)