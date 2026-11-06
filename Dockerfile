FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN python -m compileall -q /app
ENV PYTHONUNBUFFERED=1 PORT=8765 KUDRET_AUTO_SCAN=0 KUDRET_AUTO_PAPER=0
EXPOSE 8765
CMD ["python","server.py"]
