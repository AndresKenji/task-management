# Etapa 1: Construcción
FROM node:20-alpine AS build

WORKDIR /app/taskManager

COPY ./taskManager/package.json ./taskManager/package-lock.json ./

RUN npm install

COPY ./taskManager .

RUN npm run build

# Etapa 2: Servir
FROM nginx:1.25-alpine

USER root

RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx

USER nginx

COPY --chown=nginx:nginx --from=build /app/taskManager/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

ENTRYPOINT ["nginx", "-c", "/etc/nginx/nginx.conf"]
CMD ["-g", "daemon off;"]
