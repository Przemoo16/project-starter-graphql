import { expect, test } from 'vitest';

import { GraphQLError } from './graphql-error';
import { sendGraphQLAuthenticatedRequest } from './send-graphql-authenticated-request';

test(`[sendGraphQLAuthenticatedRequest function]: sends original request with the auth header`, async () => {
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

  await sendGraphQLAuthenticatedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(headersCalled).toMatchObject({
    Authorization: 'Bearer test-token',
  });
});

test(`[sendGraphQLAuthenticatedRequest function]: sends original request successfully`, async () => {
  let onUnauthorizedCalled = false;
  const onFetch = async () => {
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

  await sendGraphQLAuthenticatedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: doesn't handle non graphql errors in original request`, async () => {
  let onUnauthorizedCalled = false;
  const onFetch = async () => {
    throw new Error('Connection error');
  };
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const requestConfig = { onUnauthorized };

  await expect(
    async () =>
      await sendGraphQLAuthenticatedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(/^Connection error$/);

  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: doesn't handle non token related errors in original request`, async () => {
  let onUnauthorizedCalled = false;
  const onFetch = async () => ({
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
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const requestConfig = { onUnauthorized };

  await expect(
    async () =>
      await sendGraphQLAuthenticatedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);

  expect(onUnauthorizedCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: calls onUnauthorized callback on token related errors in original request`, async () => {
  let onFetchCalledTimes = 0;
  let onUnauthorizedCalled = false;
  let onInvalidTokensCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
    return onFetchCalledTimes === 1
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
      : {};
  };
  const onUnauthorized = async () => {
    onUnauthorizedCalled = true;
  };
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onUnauthorized, onInvalidTokens };

  await sendGraphQLAuthenticatedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(onUnauthorizedCalled).toBe(true);
  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: calls onInvalidTokens callback on onUnauthorized callback error`, async () => {
  let onFetchCalledTimes = 0;
  let onInvalidTokensCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
    return onFetchCalledTimes === 1
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
      : {};
  };
  const onUnauthorized = async () => {
    throw new Error();
  };
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onUnauthorized, onInvalidTokens };

  await sendGraphQLAuthenticatedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(onInvalidTokensCalled).toBe(true);
});

test(`[sendGraphQLAuthenticatedRequest function]: retry request with new token`, async () => {
  let onGetAuthHeaderCalledTimes = 0;
  let onFetchCalledTimes = 0;
  const headersCalled: Array<Record<string, string> | undefined> = [];
  const onFetch = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
    headersCalled.push(headers);
    onFetchCalledTimes += 1;
    return onFetchCalledTimes === 1
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
      : {};
  };
  const onGetAuthHeader = () => {
    const token =
      onGetAuthHeaderCalledTimes === 0 ? 'first-token' : 'second-token';
    onGetAuthHeaderCalledTimes += 1;
    return { Authorization: `Bearer ${token}` };
  };
  const requestConfig = { onGetAuthHeader };

  await sendGraphQLAuthenticatedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(headersCalled).toHaveLength(2);
  expect(headersCalled[0]).toMatchObject({
    Authorization: 'Bearer first-token',
  });
  expect(headersCalled[1]).toMatchObject({
    Authorization: 'Bearer second-token',
  });
});

test(`[sendGraphQLAuthenticatedRequest function]: retry request successfully`, async () => {
  let onFetchCalledTimes = 0;
  let onInvalidTokensCalled = false;
  const headersCalled: Array<Record<string, string> | undefined> = [];
  const onFetch = async (
    _url: string,
    { headers }: { headers?: Record<string, string> },
  ) => {
    headersCalled.push(headers);
    onFetchCalledTimes += 1;
    return onFetchCalledTimes === 1
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
      : {};
  };
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onInvalidTokens };

  await sendGraphQLAuthenticatedRequest(
    onFetch,
    'http://localhost',
    requestConfig,
  );

  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: doesn't handle non graphql errors in retry request`, async () => {
  let onFetchCalledTimes = 0;
  let onInvalidTokensCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
    if (onFetchCalledTimes === 1) {
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
    }
    throw new Error('Connection error');
  };
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onInvalidTokens };

  await expect(
    async () =>
      await sendGraphQLAuthenticatedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(/^Connection error$/);

  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: doesn't handle non token related errors in retry request`, async () => {
  let onFetchCalledTimes = 0;
  let onInvalidTokensCalled = false;
  const onFetch = async () => {
    onFetchCalledTimes += 1;
    return onFetchCalledTimes === 1
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
      : {
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
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onInvalidTokens };

  await expect(
    async () =>
      await sendGraphQLAuthenticatedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);

  expect(onInvalidTokensCalled).toBe(false);
});

test(`[sendGraphQLAuthenticatedRequest function]: calls onInvalidTokens callback in retry request`, async () => {
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
  const onInvalidTokens = async () => {
    onInvalidTokensCalled = true;
  };
  const requestConfig = { onInvalidTokens };

  await expect(
    async () =>
      await sendGraphQLAuthenticatedRequest(
        onFetch,
        'http://localhost',
        requestConfig,
      ),
  ).rejects.toThrowError(GraphQLError);

  expect(onInvalidTokensCalled).toBe(true);
});
