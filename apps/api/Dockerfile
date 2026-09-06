FROM python:3.12-slim

WORKDIR /repo

# Install the three business-logic packages and the API app together,
# mirroring local dev (see AGENTS.md / README "Running the backend").
COPY packages/indic_text packages/indic_text
COPY packages/audio_metrics packages/audio_metrics
COPY packages/tts_runtime packages/tts_runtime
COPY apps/api apps/api

RUN pip install --no-cache-dir \
    ./packages/indic_text \
    ./packages/audio_metrics \
    ./packages/tts_runtime \
    ./apps/api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/repo/apps/api"]
