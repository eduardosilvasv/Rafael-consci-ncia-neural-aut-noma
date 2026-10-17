FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOST=0.0.0.0
WORKDIR /app
COPY . /app
RUN useradd --system --uid 10001 rafael && mkdir -p /var/lib/rafael && chown -R rafael:rafael /app /var/lib/rafael
USER rafael
ENV RAFAEL_DATA_DIR=/var/lib/rafael/data
EXPOSE 8000
CMD ["python", "server.py"]
