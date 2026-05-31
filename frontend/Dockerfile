FROM node:22-alpine AS builder

WORKDIR /app

# Enable pnpm (lock to v10 for lockfile compatibility)
RUN corepack enable && corepack prepare pnpm@10 --activate

# Install dependencies (allow esbuild native builds)
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source and build
COPY . .
RUN pnpm vite build

# Production stage: nginx serving static files
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
