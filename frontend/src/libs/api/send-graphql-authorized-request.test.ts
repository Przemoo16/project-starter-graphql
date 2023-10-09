import { expect, test } from 'vitest';

import { GraphQLError } from './graphql-error';
import { sendGraphQLAuthorizedRequest } from './send-graphql-authorized-request';

test(`[sendGraphQLAuthorizedRequest function]: sends request with the auth header`, async () => {
  let headersCalled = null;
  const onFetch = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
    headersCalled = headers;
    return {
      data: {
        foo: 'bar',
      },
    };
  };
  const onGetAuthHeader = () => ({
    Authorization: 'Bearer test-token',
  });
  const requestConfig = { onGetAuthHeader };

  await sendGraphQLAuthorizedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(headersCalled).toMatchObject({
    Authorization: 'Bearer test-token',
  });
});

test(`[sendGraphQLAuthorizedRequest function]: sends original request successfully`, async () => {
  let onFetchCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
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

  await sendGraphQLAuthorizedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(onFetchCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendGraphQLAuthorizedRequest function]: doesn't handle non graphql errors`, async () => {
  let onFetchCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
    throw new Error('Connection error');
  };
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const requestConfig = { onUnauthorized };

  await expect(
    async () =>
      await sendGraphQLAuthorizedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(/^Connection error$/);

  expect(onFetchCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendGraphQLAuthorizedRequest function]: doesn't handle non token related errors`, async () => {
  let onFetchCalledTimes = 0;
  let onUnauthorizedCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
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
      await sendGraphQLAuthorizedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);

  expect(onFetchCalledTimes).toEqual(1);
  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendGraphQLAuthorizedRequest function]: calls onUnauthorized callback on token related errors`, async () => {
  let onUnauthorizedCalled = false;
  let onInvalidTokensCalled = false;
  const onFetch = async () => ({
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
  const onInvalidTokens = () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onUnauthorized, onInvalidTokens };

  await expect(
    async () =>
      await sendGraphQLAuthorizedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);

  expect(onUnauthorizedCalled).toBe(true);
  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendGraphQLAuthorizedRequest function]: calls onInvalidTokens callback on onUnauthorized callback error`, async () => {
  let onInvalidTokensCalled = false;
  const onFetch = async () => ({
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
  const onInvalidTokens = () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onUnauthorized, onInvalidTokens };

  await expect(
    async () =>
      await sendGraphQLAuthorizedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);
  expect(onInvalidTokensCalled).toBe(true);
});

test(`[sendGraphQLAuthorizedRequest function]: retry original request with new token`, async () => {
  let onGetAuthHeaderCalledTimes = 0;
  const headersCalled: Array<Record<string, string> | undefined> = [];
  const onFetch = async (
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
  const onGetAuthHeader = () => {
    const token =
      onGetAuthHeaderCalledTimes === 0 ? 'first-token' : 'second-token';
    onGetAuthHeaderCalledTimes += 1;
    return { Authorization: `Bearer ${token}` };
  };
  const requestConfig = { onGetAuthHeader };

  await expect(
    async () =>
      await sendGraphQLAuthorizedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);

  expect(headersCalled).toHaveLength(2);
  expect(headersCalled[0]).toMatchObject({
    Authorization: 'Bearer first-token',
  });
  expect(headersCalled[1]).toMatchObject({
    Authorization: 'Bearer second-token',
  });
});
