import { expect, test, vi } from 'vitest';

import { getApiURL } from './get-api-url';

test(`[getApiURL function]: returns default server URL`, () => {
  const url = getApiURL(true);

  expect(url).toEqual('http://proxy/graphql');
});

test(`[getApiURL function]: returns default client URL`, () => {
  const url = getApiURL(false);

  expect(url).toEqual('http://localhost:5173/graphql');
});

test(`[getApiURL function]: returns server URL from env variable`, () => {
  vi.stubEnv('VITE_SERVER_API_URL', 'http://server-url');

  const url = getApiURL(true);

  expect(url).toEqual('http://server-url');
});

test(`[getApiURL function]: returns client URL from env variable`, () => {
  vi.stubEnv('VITE_CLIENT_API_URL', 'http://client-url');

  const url = getApiURL(false);

  expect(url).toEqual('http://client-url');
});
