# ---- Stage 1: build the static SPA ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
# npm install (not `npm ci`) so the build resolves platform-specific optional deps
# (e.g. Tailwind v4's native binary) that the macOS-generated lockfile omits for linux.
RUN npm install --no-audit --no-fund
COPY . .
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

# ---- Stage 2: serve the static build with nginx ----
FROM nginx:alpine AS serve
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
