FROM node:20-slim AS builder
WORKDIR /repo/apps/web
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install
COPY apps/web .
RUN npm run build

FROM node:20-slim
WORKDIR /repo/apps/web
ENV NODE_ENV=production
COPY --from=builder /repo/apps/web/.next ./.next
COPY --from=builder /repo/apps/web/public ./public
COPY --from=builder /repo/apps/web/package.json ./package.json
COPY --from=builder /repo/apps/web/node_modules ./node_modules

EXPOSE 3000
CMD ["npm", "run", "start"]
