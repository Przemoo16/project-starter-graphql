FROM mcr.microsoft.com/playwright:v1.40.0-jammy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

RUN corepack enable

COPY ./package.json ./.yarnrc.yml ./yarn.lock ./
RUN yarn install --immutable \
    && yarn cache clean

COPY . .

CMD ["npx", "playwright", "test"]
