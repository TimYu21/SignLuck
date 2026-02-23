FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
# Запуск через npm run dev с пробросом хоста
CMD ["npm", "run", "dev", "--", "--host"]