FROM node:20.5-slim as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

EXPOSE 5173


FROM base as deps

COPY ./package.json ./yarn.lock ./
RUN yarn install --frozen-lockfile \
    && yarn cache clean

COPY . .


FROM deps AS dev

CMD ["yarn", "dev"]


FROM deps as build

RUN yarn build


FROM base

COPY --from=build /opt/app/node_modules ./node_modules
COPY --from=build /opt/app/dist ./dist
COPY --from=build /opt/app/server ./server

CMD ["node", "server/entry.node-server"]
