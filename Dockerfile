FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY strategy_debate.py app.py api_server.py start.sh ./
COPY webauthn_component/ ./webauthn_component/

RUN mkdir -p /app/data && chmod +x start.sh

EXPOSE 8501 8502

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["./start.sh"]
