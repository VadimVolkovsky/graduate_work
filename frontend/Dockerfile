
# Используем базовый образ Nginx
FROM nginx:1.25.3

# Копируем наш index.html в стандартную директорию Nginx
COPY ./frontend/index.html /usr/share/nginx/html/
COPY ./frontend/login.html /usr/share/nginx/html/

# Открываем порт 8080
EXPOSE 8080

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]