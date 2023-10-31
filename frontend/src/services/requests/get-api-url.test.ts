import { expect, test, vi } from 'vitest';

import { getApiGraphQLUrl } from './get-api-url';

test(`[getApiGraphQLUrl function]: returns default server URL`, () => {
  const url = getApiGraphQLUrl(true);

  expect(url).toEqual('http://proxy/api/graphql');
});

test(`[getApiGraphQLUrl function]: returns default client URL`, () => {
  const url = getApiGraphQLUrl(false);

  expect(url).toEqual('http://localhost:5173/api/graphql');
});

test(`[getApiGraphQLUrl function]: returns server URL from env variable`, () => {
  vi.stubEnv(
    'VITE_SERVER_BACKEND_GRAPHQL_URL',
    'http://server-url/api/graphql',
  );

  const url = getApiGraphQLUrl(true);

  expect(url).toEqual('http://server-url/api/graphql');
});

test(`[getApiGraphQLUrl function]: returns client URL from env variable`, () => {
  vi.stubEnv(
    'VITE_CLIENT_BACKEND_GRAPHQL_URL',
    'http://client-url/api/graphql',
  );

  const url = getApiGraphQLUrl(false);

  expect(url).toEqual('http://client-url/api/graphql');
});
