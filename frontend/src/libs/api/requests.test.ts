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
  ): Promise<Record<string, Record<string, string>>> => {
    return {
      data: {
        foo: 'bar',
      },
    };
  };

  const data = await sendRequest(fetcher, "http://localhost'", 'test-query');

  expect(data).toEqual({ foo: 'bar' });
});

test(`[sendRequest function]: throws error`, async () => {
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[]>> => {
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
  ): Promise<Record<string, GraphQLError[]>> => {
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

test(`[sendAuthorizedRequest function]: sends request without an auth header`, async () => {
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

  const accessTokenGetter = async (): Promise<null> => null;

  await sendAuthorizedRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    accessTokenGetter,
  );

  expect(calledHeaders).toEqual({ 'Content-Type': 'application/json' });
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
  const accessTokenGetter = async (): Promise<string> => 'test-token';

  await sendAuthorizedRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    accessTokenGetter,
  );

  expect(calledHeaders).toEqual({
    'Content-Type': 'application/json',
    Authorization: 'Bearer test-token',
  });
});

test(`[sendAuthorizedRequest function]: sends original request successfully`, async () => {
  let onAuthorizedCalled = false;
  let onInvalidTokensCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, Record<string, string>>> => {
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const onAuthorized = async (): Promise<void> => {
    onAuthorizedCalled = true;
  };
  const onInvalidTokens = async (): Promise<void> => {
    onInvalidTokensCalled = true;
  };

  await sendAuthorizedRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    async (): Promise<null> => null,
    onAuthorized,
    onInvalidTokens,
  );

  expect(onAuthorizedCalled).toBe(false);
  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: calls onAuthorized callback`, async () => {
  let fetcherCalledTimes = 0;
  let onAuthorizedCalled = false;
  let onInvalidTokensCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[] | Record<string, string>>> => {
    const response: Record<string, GraphQLError[] | Record<string, string>> =
      fetcherCalledTimes === 0
        ? {
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
          }
        : { data: { foo: 'bar' } };
    fetcherCalledTimes += 1;
    return response;
  };
  const onAuthorized = async (): Promise<void> => {
    onAuthorizedCalled = true;
  };
  const onInvalidTokens = async (): Promise<void> => {
    onInvalidTokensCalled = true;
  };

  await sendAuthorizedRequest(
    fetcher,
    'http://localhost',
    'test-query',
    undefined,
    async (): Promise<null> => null,
    onAuthorized,
    onInvalidTokens,
  );

  expect(onAuthorizedCalled).toBe(true);
  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: calls onInvalidTokens callback`, async () => {
  let onInvalidTokensCalled = false;
  const fetcher = async (
    _url: string,
    _method?: string,
    _body?: string,
    _headers?: Record<string, string>,
  ): Promise<Record<string, GraphQLError[]>> => {
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
  const onAuthorized = async (): Promise<void> => {
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
        async (): Promise<null> => null,
        onAuthorized,
        onInvalidTokens,
      ),
  ).rejects.toThrowError(RequestError);
  expect(onInvalidTokensCalled).toBe(true);
});
