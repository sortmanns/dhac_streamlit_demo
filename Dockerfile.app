FROM python:3.10-slim

# Expose port you want your app on
EXPOSE 8501

# Upgrade pip, install requirements, and clean up in one layer
COPY requirements.txt .
RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Copy app code
COPY src /src
# COPY .streamlit/secrets.toml /src/.streamlit/secrets.toml
# Set working directory
WORKDIR /src

# Run with multi-stage build considerations (if applicable)
ENTRYPOINT ["streamlit", "run", "./dhac_streamlit_demo/propel_auth_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=False", "--server.enableXsrfProtection=false"]


