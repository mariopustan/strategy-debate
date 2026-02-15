#!/bin/sh
# Start both Streamlit (8501) and the REST API (8502)
uvicorn api_server:app --host 0.0.0.0 --port 8502 &
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
