# Проект по сбору данных NFT

## Описание

Этот проект собирает данные о NFT с различных источников, обрабатывает их и сохраняет в файл `nft_data.json`. Программа выполняется в асинхронном цикле и обновляет данные каждые 8 секунд.

## Структура проекта

- `api_clients.py`: Клиенты для взаимодействия с различными API.
- `data_aggregator.py`: Класс `DataAggregator`, который объединяет данные из разных источников.
- `main.py`: Точка входа в приложение.
- `utils.py`: Вспомогательные функции и настройки логирования.
- `config.py`: Конфигурационные параметры и константы.
- `requirements.txt`: Список зависимостей проекта.

## Установка и запуск

1. Клонируйте репозиторий или скопируйте файлы проекта в отдельную директорию.
2. Создайте виртуальное окружение (рекомендуется):

   ```bash
   python -m venv venv
   ```
