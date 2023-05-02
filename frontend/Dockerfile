FROM node:20.0-slim as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app/package.json ./app/yarn.lock ./
RUN yarn install --frozen-lockfile \
    && yarn cache clean

COPY ./app .


FROM base AS dev

EXPOSE 5173

CMD ["yarn", "dev"]


FROM base as build

RUN yarn build


FROM nginx:1.23.4

COPY --from=build /app/dist /usr/share/nginx/html
