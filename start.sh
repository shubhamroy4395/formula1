#!/bin/bash
# Startup script for Streamlit Cloud

# Ensure paths are set correctly
export PATH=$PATH:/home/adminuser/.local/bin

# Run health check first
python streamlit_app.py healthcheck

# Start Streamlit server
streamlit run streamlit_app.py 