# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Указываем порт, который будет использовать приложение
EXPOSE 53474

# Команда для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:53474"]