import { expect, test, vi } from 'vitest';

import { getApiURL, RequestError, sendRequest } from './requests';

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

test(`[sendRequest function]: returns data`, async () => {
  const successFetcher = async (
    _url: string,
  ): Promise<Record<string, Record<string, string>>> => {
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const url = 'http://localhost';
  const query = 'test-query';

  const data = await sendRequest(successFetcher, url, query);

  expect(data).toEqual({ foo: 'bar' });
});

test(`[sendRequest function]: throws error`, async () => {
  const errorFetcher = async (
    _url: string,
  ): Promise<Record<string, Record<string, string>>> => {
    return {
      errors: {
        foo: 'bar',
      },
    };
  };
  const url = 'http://localhost';
  const query = 'test-query';

  await expect(
    async () => await sendRequest(errorFetcher, query, url),
  ).rejects.toThrowError(RequestError);
});

test(`[sendRequest function]: throws error with error details included`, async () => {
  const errorFetcher = async (
    _url: string,
  ): Promise<Record<string, Record<string, string>>> => {
    return {
      errors: {
        foo: 'bar',
      },
    };
  };
  const url = 'http://localhost';
  const query = 'test-query';

  try {
    await sendRequest(errorFetcher, query, url);
    throw new Error();
  } catch (e) {
    const error = e as RequestError;
    expect(error.errors).toEqual({ foo: 'bar' });
  }
});
