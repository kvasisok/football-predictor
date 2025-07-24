#!/bin/bash
cd /storage/emulated/0/football-predictor

# Добавляем все изменения
git add .

# Создаем коммит с датой
git commit -m "Автобэкап $(date +'%d.%m.%Y %H:%M')" || echo "Нет изменений для коммита"

# Пушим на GitHub
git push origin main
