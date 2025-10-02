FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser
USER botuser

CMD ["python", "bot.py"]