import { expect, test } from 'vitest';

import { GraphQLError } from '~/libs/api/graphql-error';

import { sendGraphQLRequest } from './send-graphql-request';

test(`[sendGraphQLRequest function]: returns data`, async () => {
  const onFetch = async () => ({
    data: {
      foo: 'bar',
    },
  });

  const data = await sendGraphQLRequest(onFetch, "http://localhost'");

  expect(data).toEqual({ foo: 'bar' });
});

test(`[sendGraphQLRequest function]: throws error`, async () => {
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
    async () => await sendGraphQLRequest(onFetch, 'http://localhost'),
  ).rejects.toThrowError(GraphQLError);
});

test(`[sendGraphQLRequest function]: throws error with error details included`, async () => {
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
    await sendGraphQLRequest(onFetch, 'http://localhost');
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

test(`[sendGraphQLRequest function]: sends serialized body`, async () => {
  let bodyCalled = null;
  const onFetch = async (
    _query: string,
    { body }: { body?: BodyInit | null },
  ) => {
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

  await sendGraphQLRequest(onFetch, 'http://localhost', requestConfig);

  expect(bodyCalled).toEqual(
    '{"query":"test-query","variables":{"foo":"bar"}}',
  );
});

test(`[sendGraphQLRequest function]: uses Content-Type header by default`, async () => {
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

  await sendGraphQLRequest(onFetch, 'http://localhost');

  expect(headersCalled).toEqual({
    'Content-Type': 'application/json',
  });
});

test(`[sendGraphQLRequest function]: uses the custom headers with the default ones`, async () => {
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

  await sendGraphQLRequest(onFetch, 'http://localhost', requestConfig);

  expect(headersCalled).toEqual({
    'Content-Type': 'application/json',
    Test: 'Header',
  });
});
