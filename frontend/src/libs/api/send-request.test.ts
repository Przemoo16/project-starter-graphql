import { expect, test } from 'vitest';

import { GraphQLError } from '~/libs/api/graphql-error';

import { sendRequest } from './send-request';

test(`[sendRequest function]: returns data`, async () => {
  const onFetch = async () => ({
    data: {
      foo: 'bar',
    },
  });

  const data = await sendRequest(onFetch, "http://localhost'");

  expect(data).toEqual({ foo: 'bar' });
});

test(`[sendRequest function]: throws error`, async () => {
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
  await expect(
    async () => await sendRequest(onFetch, 'http://localhost'),
  ).rejects.toThrowError(GraphQLError);
});

test(`[sendRequest function]: throws error with error details included`, async () => {
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

  try {
    await sendRequest(onFetch, 'http://localhost');
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
  let bodyCalled = null;
  const onFetch = async (_query: string, { body }: { body?: string }) => {
    bodyCalled = body;
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

  await sendRequest(onFetch, 'http://localhost', requestConfig);

  expect(bodyCalled).toEqual(
    '{"query":"test-query","variables":{"foo":"bar"}}',
  );
});

test(`[sendRequest function]: uses Content-Type header by default`, async () => {
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

  await sendRequest(onFetch, 'http://localhost');

  expect(headersCalled).toEqual({
    'Content-Type': 'application/json',
  });
});

test(`[sendRequest function]: uses the custom headers with the default ones`, async () => {
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
  const requestConfig = { headers: { Test: 'Header' } };

  await sendRequest(onFetch, 'http://localhost', requestConfig);

  expect(headersCalled).toEqual({
    'Content-Type': 'application/json',
    Test: 'Header',
  });
});
