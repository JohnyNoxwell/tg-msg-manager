FROM python:3.12-slim

ENV HOME=/root \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/tg-msg-manager

COPY pyproject.toml README.md LICENSE ./
COPY tg_msg_manager ./tg_msg_manager

RUN python -m pip install --no-cache-dir .

WORKDIR /root/TG_MSG_MANAGER

ENTRYPOINT ["tg-msg-manager"]
