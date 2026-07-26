FROM node:24.15.0-alpine AS build

WORKDIR /app
RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build

FROM nginx:1.29-alpine AS runtime

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build --chown=101:101 /app/dist/frontend/browser /usr/share/nginx/html

USER 101:101

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/health

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
