FROM mcr.microsoft.com/playwright:v1.40.0-jammy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY ./package.json ./yarn.lock ./
RUN yarn install --frozen-lockfile \
    && yarn cache clean

COPY . .

CMD ["npx", "playwright", "test"]
