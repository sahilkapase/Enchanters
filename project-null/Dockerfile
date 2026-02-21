# ── Farmer App ──
FROM node:20-alpine AS farmer-build
WORKDIR /app
COPY farmer-app/package*.json ./
RUN npm ci
COPY farmer-app/ ./
RUN npm run build

# ── Service Portal ──
FROM node:20-alpine AS portal-build
WORKDIR /app
COPY service-portal/package*.json ./
RUN npm ci
COPY service-portal/ ./
RUN npm run build

# ── Nginx ──
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=farmer-build /app/dist /usr/share/nginx/farmer-app
COPY --from=portal-build /app/dist /usr/share/nginx/service-portal
EXPOSE 80 81
CMD ["nginx", "-g", "daemon off;"]
