import { expect, test, vi } from 'vitest';

import { getClientGraphQLApiUrl } from './get-client-graphql-api-url';

test(`[getClientGraphQLApiUrl function]: returns default URL`, () => {
  const url = getClientGraphQLApiUrl();

  expect(url).toEqual('/api/graphql');
});

test(`[getClientGraphQLApiUrl function]: returns URL from env variable`, () => {
  vi.stubEnv('PUBLIC_CLIENT_GRAPHQL_API_URL', 'http://client-url/api/graphql');

  const url = getClientGraphQLApiUrl();

  expect(url).toEqual('http://client-url/api/graphql');
});
