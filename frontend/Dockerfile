# Intensicare Clinical Dashboard — Frontend
# Multi-stage build: dev (with Vite dev server) and production (nginx)

# ---- Development Stage ----
FROM node:20-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]


# ---- Build Stage ----
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build


# ---- Production Stage ----
FROM nginx:1.27-alpine AS production

# Create temp directories and set ownership for nginx user (uid 101)
RUN mkdir -p /var/cache/nginx/client_temp /var/cache/nginx/proxy_temp \
    && chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx

COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# Drop privileges — run as the built-in nginx user (uid 101)
USER nginx

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
