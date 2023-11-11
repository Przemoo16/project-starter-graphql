import { expect, test } from 'vitest';

import { getServerGraphQLApiUrl } from './get-server-graphql-api-url';

test(`[getServerGraphQLApiUrl function]: returns default URL`, () => {
  class EnvGetter {
    get = () => undefined;
  }
  const envGetter = new EnvGetter();

  const url = getServerGraphQLApiUrl(envGetter);

  expect(url).toEqual('http://proxy/api/graphql');
});

test(`[getServerGraphQLApiUrl function]: returns URL from env variable`, () => {
  class EnvGetter {
    get = (key: string) => {
      const env = { SERVER_GRAPHQL_API_URL: 'http://server-url/api/graphql' };
      return env[key as keyof typeof env];
    };
  }
  const envGetter = new EnvGetter();

  const url = getServerGraphQLApiUrl(envGetter);

  expect(url).toEqual('http://server-url/api/graphql');
});
