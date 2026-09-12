# Imagen del tablero. El contexto de build es ui/, no la raiz del repositorio:
#
#   docker build -t airlines-ui ui/
#   docker run -p 8080:80 airlines-ui
#
# VITE_API_URL se resuelve en tiempo de construccion. Vite reemplaza la
# variable dentro del bundle, asi que no puede cambiarse al arrancar el
# contenedor: por eso viaja como argumento de build y no como variable de
# entorno en tiempo de ejecucion.

FROM node:24-alpine AS build

WORKDIR /app

# Primero el manifiesto: cambiar un componente no debe reinstalar las
# dependencias.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

ARG VITE_API_URL=http://localhost:8002
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build


FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1
