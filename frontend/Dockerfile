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


FROM base AS dev

EXPOSE 5173

CMD ["yarn", "dev"]


FROM base as build

RUN yarn build


FROM nginx:1.25

COPY --from=build /opt/app/dist /usr/share/nginx/html
