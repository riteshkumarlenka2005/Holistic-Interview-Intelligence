FROM node:20-alpine AS base
WORKDIR /app

# Install dependencies
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm install

# Build the application
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Use the Node adapter config instead of Vercel for Docker builds
RUN cp astro.config.docker.mjs astro.config.mjs
RUN npm run build

# Production image
FROM base AS runtime
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY package.json ./

ENV HOST=0.0.0.0
ENV PORT=4321
ENV NODE_ENV=production

EXPOSE 4321

CMD ["node", "./dist/server/entry.mjs"]
