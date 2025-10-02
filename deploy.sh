#!/bin/bash

set -e  # Выход при ошибке

echo "🚀 Starting deployment..."

# Переменные
BOT_DIR="/opt/movies-booksBot"
SERVICE_NAME="movies-booksBot"

# Проверка существования директории
if [ ! -d "$BOT_DIR" ]; then
    echo "📁 Creating bot directory..."
    sudo mkdir -p $BOT_DIR
    sudo chown $USER:$USER $BOT_DIR
fi

cd $BOT_DIR

# Остановка сервиса если запущен
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "⏹️ Stopping current bot..."
    sudo systemctl stop $SERVICE_NAME
fi

# Копирование файлов (если не используется git pull)
echo "📦 Copying files..."
cp -f ../movies-booksBot/src/bot.py .
cp -f ../movies-booksBot/requirements.txt .
cp -f ../movies-booksBot/docker-compose.yml .

# Установка зависимостей
echo "📚 Installing dependencies..."
pip3 install -r requirements.txt

# Настройка прав
chmod +x bot.py

# Запуск сервиса
echo "🔧 Setting up systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Telegram Movies & Books Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
Environment=TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
ExecStart=/usr/bin/python3 $BOT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd и запуск
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Проверка статуса
echo "✅ Checking service status..."
sleep 3
sudo systemctl status $SERVICE_NAME --no-pager

echo "🎉 Deployment completed!"