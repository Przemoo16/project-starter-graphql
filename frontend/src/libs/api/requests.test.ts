import { expect, test, vi } from 'vitest';

import {
  getApiURL,
  type GraphQLError,
  RequestError,
  sendAuthorizedRequest,
  sendRequest,
} from './requests';

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
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => ({
    data: {
      foo: 'bar',
    },
  });

  const data = await sendRequest(fetcher, "http://localhost'", 'test-query');

  expect(data).toEqual({ foo: 'bar' });
});

test(`[sendRequest function]: throws error`, async () => {
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[]>> => ({
    errors: [
      {
        message: 'Error',
        locations: [
          {
            line: 1,
            column: 1,
          },
        ],
        path: ['test'],
      },
    ],
  });

  await expect(
    async () => await sendRequest(fetcher, 'http://localhost', 'test-query'),
  ).rejects.toThrowError(RequestError);
});

test(`[sendRequest function]: throws error with error details included`, async () => {
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[]>> => ({
    errors: [
      {
        message: 'Error',
        locations: [
          {
            line: 1,
            column: 1,
          },
        ],
        path: ['test'],
      },
    ],
  });

  try {
    await sendRequest(fetcher, 'http://localhost', 'test-query');
    throw new Error();
  } catch (e) {
    const error = e as RequestError;
    expect(error.errors).toEqual([
      {
        message: 'Error',
        locations: [
          {
            line: 1,
            column: 1,
          },
        ],
        path: ['test'],
      },
    ]);
  }
});

test(`[sendRequest function]: sends serialized body`, async () => {
  let calledBody: string | undefined;
  const fetcher = async (
    _url: string,
    _method?: string,
    body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => {
    calledBody = body;
    return {
      data: {
        foo: 'bar',
      },
    };
  };

  await sendRequest(fetcher, 'http://localhost', 'test-query', { foo: 'bar' });

  expect(calledBody).toEqual(
    '{"query":"test-query","variables":{"foo":"bar"}}',
  );
});

test(`[sendRequest function]: uses Content-Type header by default`, async () => {
  let calledHeaders: Record<string, string> | undefined = {};
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => {
    calledHeaders = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };

  await sendRequest(fetcher, 'http://localhost', 'test-query');

  expect(calledHeaders).toEqual({
    'Content-Type': 'application/json',
  });
});

test(`[sendRequest function]: uses the custom headers with the default ones`, async () => {
  let calledHeaders: Record<string, string> | undefined = {};
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => {
    calledHeaders = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const headers = { Test: 'Header' };

  await sendRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    headers,
  );

  expect(calledHeaders).toEqual({
    'Content-Type': 'application/json',
    Test: 'Header',
  });
});

test(`[sendAuthorizedRequest function]: sends request with the auth header`, async () => {
  let calledHeaders: Record<string, string> | undefined = {};
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => {
    calledHeaders = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const getAuthHeader = async (): Promise<Record<string, string>> => ({
    Authorization: 'Bearer test-token',
  });

  await sendAuthorizedRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    getAuthHeader,
  );

  expect(calledHeaders).toMatchObject({
    Authorization: 'Bearer test-token',
  });
});

test(`[sendAuthorizedRequest function]: sends original request successfully`, async () => {
  let fetcherCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => {
    fetcherCalledTimes += 1;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const getAuthHeader = async (): Promise<Record<string, string>> => ({
    Authorization: 'Bearer test-token',
  });
  const onUnauthorized = async (): Promise<void> => {
    onUnauthorizedCalled = true;
  };

  await sendAuthorizedRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    getAuthHeader,
    onUnauthorized,
  );

  expect(fetcherCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: doesn't handle non token related errors`, async () => {
  let fetcherCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[] | Record<string, string>>> => {
    fetcherCalledTimes += 1;
    return {
      errors: [
        {
          message: 'Error',
          locations: [
            {
              line: 1,
              column: 1,
            },
          ],
          path: ['test'],
        },
      ],
    };
  };
  const getAuthHeader = async (): Promise<Record<string, string>> => ({
    Authorization: 'Bearer test-token',
  });
  const onUnauthorized = async (): Promise<void> => {
    onUnauthorizedCalled = true;
  };

  await expect(
    async () =>
      await sendAuthorizedRequest(
        fetcher,
        'http://localhost',
        'test-query',
        undefined,
        getAuthHeader,
        onUnauthorized,
      ),
  ).rejects.toThrowError(RequestError);

  expect(fetcherCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: calls onUnauthorized callback on token related errors`, async () => {
  let onUnauthorizedCalled = false;
  let onInvalidTokensCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[] | Record<string, string>>> => ({
    errors: [
      {
        message: 'Invalid token',
        locations: [
          {
            line: 1,
            column: 1,
          },
        ],
        path: ['test'],
      },
    ],
  });
  const getAuthHeader = async (): Promise<Record<string, string>> => ({
    Authorization: 'Bearer test-token',
  });
  const onUnauthorized = async (): Promise<void> => {
    onUnauthorizedCalled = true;
  };
  const onInvalidTokens = async (): Promise<void> => {
    onInvalidTokensCalled = true;
  };

  await expect(
    async () =>
      await sendAuthorizedRequest(
        fetcher,
        'http://localhost',
        'test-query',
        undefined,
        getAuthHeader,
        onUnauthorized,
        onInvalidTokens,
      ),
  ).rejects.toThrowError(RequestError);

  expect(onUnauthorizedCalled).toBe(true);
  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: calls onInvalidTokens callback on onUnauthorized callback error`, async () => {
  let onInvalidTokensCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[]>> => ({
    errors: [
      {
        message: 'Invalid token',
        locations: [
          {
            line: 1,
            column: 1,
          },
        ],
        path: ['test'],
      },
    ],
  });
  const getAuthHeader = async (): Promise<Record<string, string>> => ({
    Authorization: 'Bearer test-token',
  });
  const onUnauthorized = async (): Promise<void> => {
    throw new Error();
  };
  const onInvalidTokens = async (): Promise<void> => {
    onInvalidTokensCalled = true;
  };

  await expect(
    async () =>
      await sendAuthorizedRequest(
        fetcher,
        'http://localhost',
        'test-query',
        undefined,
        getAuthHeader,
        onUnauthorized,
        onInvalidTokens,
      ),
  ).rejects.toThrowError(RequestError);
  expect(onInvalidTokensCalled).toBe(true);
});

test(`[sendAuthorizedRequest function]: retry original request with new token`, async () => {
  let getAuthHeaderCalledTimes = 0;
  const headersCalled: Array<Record<string, string> | undefined> = [];
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[]>> => {
    headersCalled.push(headers);
    return {
      errors: [
        {
          message: 'Invalid token',
          locations: [
            {
              line: 1,
              column: 1,
            },
          ],
          path: ['test'],
        },
      ],
    };
  };
  const getAuthHeader = async (): Promise<Record<string, string>> => {
    const token =
      getAuthHeaderCalledTimes === 0 ? 'first-token' : 'second-token';
    getAuthHeaderCalledTimes += 1;
    return { Authorization: `Bearer ${token}` };
  };

  await expect(
    async () =>
      await sendAuthorizedRequest(
        fetcher,
        'http://localhost',
        'test-query',
        undefined,
        getAuthHeader,
      ),
  ).rejects.toThrowError(RequestError);

  expect(headersCalled).toHaveLength(2);
  expect(headersCalled[0]).toMatchObject({
    Authorization: 'Bearer first-token',
  });
  expect(headersCalled[1]).toMatchObject({
    Authorization: 'Bearer second-token',
  });
});
