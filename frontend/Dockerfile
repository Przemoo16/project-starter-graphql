FROM node:20.0-slim as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY ./package.json ./yarn.lock ./
RUN yarn install --frozen-lockfile \
    && yarn cache clean

COPY . .

EXPOSE 5173


FROM base AS dev

CMD ["yarn", "dev"]


FROM base as build

RUN yarn build


FROM node:20.0-slim

WORKDIR /opt/app

COPY --from=build /opt/app/node_modules ./node_modules
COPY --from=build /opt/app/dist ./dist
COPY --from=build /opt/app/server ./server

CMD ["node", "server/entry.node-server"]
