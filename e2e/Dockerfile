FROM mcr.microsoft.com/playwright:v1.40.0-jammy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

RUN corepack enable

COPY ./package.json ./yarn.lock ./
# When using yarn PnP, the PnP loader directly references packages via their cache path
# hadolint ignore=DL3060
RUN yarn install --immutable

COPY . .

CMD ["yarn", "playwright", "test"]
