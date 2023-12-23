FROM node:20.5-slim as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

EXPOSE 80


FROM base as deps

RUN corepack enable

COPY ./package.json ./.yarnrc.yml ./yarn.lock ./
RUN yarn install --immutable \
    && yarn cache clean

COPY . .


FROM deps AS dev

CMD ["yarn", "run", "dev"]


FROM deps as build

RUN yarn run build


FROM base

COPY --from=build /opt/app/node_modules ./node_modules
COPY --from=build /opt/app/dist ./dist
COPY --from=build /opt/app/server ./server

CMD ["node", "server/entry.node-server"]
