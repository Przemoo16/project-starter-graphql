import { expect, test, vi } from 'vitest';

import { getApiURL } from './urls';

test(`[getApiURL function]: returns default server URL`, async () => {
  const url = await getApiURL(true);

  expect(url).toEqual('http://proxy/graphql');
});

test(`[getApiURL function]: returns default client URL`, async () => {
  const url = await getApiURL(false);

  expect(url).toEqual('http://localhost:5173/graphql');
});

test(`[getApiURL function]: returns server URL from env variable`, async () => {
  vi.stubEnv('VITE_SERVER_API_URL', 'http://server-url');

  const url = await getApiURL(true);

  expect(url).toEqual('http://server-url');
});

test(`[getApiURL function]: returns client URL from env variable`, async () => {
  vi.stubEnv('VITE_CLIENT_API_URL', 'http://client-url');

  const url = await getApiURL(false);

  expect(url).toEqual('http://client-url');
});
