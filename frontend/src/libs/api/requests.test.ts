import { expect, test } from 'vitest';

import { GraphQLError } from './errors';
import { sendAuthorizedRequest, sendRequest } from './requests';

test(`[sendRequest function]: returns data`, async () => {
  const fetcher = async () => ({
    data: {
      foo: 'bar',
    },
  });

  const data = await sendRequest(fetcher, "http://localhost'");

  expect(data).toEqual({ foo: 'bar' });
});

test(`[sendRequest function]: throws error`, async () => {
  const fetcher = async () => ({
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
    async () => await sendRequest(fetcher, 'http://localhost'),
  ).rejects.toThrowError(GraphQLError);
});

test(`[sendRequest function]: throws error with error details included`, async () => {
  const fetcher = async () => ({
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
    await sendRequest(fetcher, 'http://localhost');
    throw new Error();
  } catch (e) {
    const error = e as GraphQLError;
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
  const fetcher = async (_query: string, { body }: { body?: string }) => {
    calledBody = body;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const requestConfig = {
    query: 'test-query',
    variables: { foo: 'bar' },
  };

  await sendRequest(fetcher, 'http://localhost', requestConfig);

  expect(calledBody).toEqual(
    '{"query":"test-query","variables":{"foo":"bar"}}',
  );
});

test(`[sendRequest function]: uses Content-Type header by default`, async () => {
  let calledHeaders: Record<string, string> | undefined = {};
  const fetcher = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
    calledHeaders = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };

  await sendRequest(fetcher, 'http://localhost');

  expect(calledHeaders).toEqual({
    'Content-Type': 'application/json',
  });
});

test(`[sendRequest function]: uses the custom headers with the default ones`, async () => {
  let calledHeaders: Record<string, string> | undefined = {};
  const fetcher = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
    calledHeaders = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const requestConfig = { headers: { Test: 'Header' } };

  await sendRequest(fetcher, 'http://localhost', requestConfig);

  expect(calledHeaders).toEqual({
    'Content-Type': 'application/json',
    Test: 'Header',
  });
});

test(`[sendAuthorizedRequest function]: sends request with the auth header`, async () => {
  let calledHeaders: Record<string, string> | undefined = {};
  const fetcher = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
    calledHeaders = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const getAuthHeader = async () => ({
    Authorization: 'Bearer test-token',
  });
  const requestConfig = { getAuthHeader };

  await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig);

  expect(calledHeaders).toMatchObject({
    Authorization: 'Bearer test-token',
  });
});

test(`[sendAuthorizedRequest function]: sends original request successfully`, async () => {
  let fetcherCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const fetcher = async () => {
    fetcherCalledTimes += 1;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const requestConfig = { onUnauthorized };

  await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig);

  expect(fetcherCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: doesn't handle non graphql errors`, async () => {
  let fetcherCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const fetcher = async () => {
    fetcherCalledTimes += 1;
    throw new Error('Connection error');
  };
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const requestConfig = { onUnauthorized };

  await expect(
    async () =>
      await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig),
  ).rejects.toThrowError(/^Connection error$/);

  expect(fetcherCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: doesn't handle non token related errors`, async () => {
  let fetcherCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const fetcher = async () => {
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
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const requestConfig = { onUnauthorized };

  await expect(
    async () =>
      await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig),
  ).rejects.toThrowError(GraphQLError);

  expect(fetcherCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: calls onUnauthorized callback on token related errors`, async () => {
  let onUnauthorizedCalled = false;
  let onInvalidTokensCalled = false;
  const fetcher = async () => ({
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
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onUnauthorized, onInvalidTokens };

  await expect(
    async () =>
      await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig),
  ).rejects.toThrowError(GraphQLError);

  expect(onUnauthorizedCalled).toBe(true);
  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendAuthorizedRequest function]: calls onInvalidTokens callback on onUnauthorized callback error`, async () => {
  let onInvalidTokensCalled = false;
  const fetcher = async () => ({
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
  const onUnauthorized = async () => {
    throw new Error();
  };
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onUnauthorized, onInvalidTokens };

  await expect(
    async () =>
      await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig),
  ).rejects.toThrowError(GraphQLError);
  expect(onInvalidTokensCalled).toBe(true);
});

test(`[sendAuthorizedRequest function]: retry original request with new token`, async () => {
  let getAuthHeaderCalledTimes = 0;
  const headersCalled: Array<Record<string, string> | undefined> = [];
  const fetcher = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
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
  const getAuthHeader = async () => {
    const token =
      getAuthHeaderCalledTimes === 0 ? 'first-token' : 'second-token';
    getAuthHeaderCalledTimes += 1;
    return { Authorization: `Bearer ${token}` };
  };
  const requestConfig = { getAuthHeader };

  await expect(
    async () =>
      await sendAuthorizedRequest(fetcher, 'http://localhost', requestConfig),
  ).rejects.toThrowError(GraphQLError);

  expect(headersCalled).toHaveLength(2);
  expect(headersCalled[0]).toMatchObject({
    Authorization: 'Bearer first-token',
  });
  expect(headersCalled[1]).toMatchObject({
    Authorization: 'Bearer second-token',
  });
});
