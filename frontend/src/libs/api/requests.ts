import { $ } from '@builder.io/qwik';

import { GraphQLError } from './errors';

export type Fetcher = (
  url: string,
  config: {
    method?: string;
    body?: string;
    headers?: Record<string, string>;
  },
) => Promise<any>;

export interface RequestConfig {
  query?: string;
  variables?: Record<string, unknown>;
  headers?: Record<string, string>;
}

export interface AuthorizedRequestProps extends Omit<RequestConfig, 'headers'> {
  onGetAuthHeader?: () => Promise<Record<string, string>>;
  onUnauthorized?: () => Promise<void>;
  onInvalidTokens?: () => Promise<void>;
}

export const sendRequest = $(
  async (
    onFetch: Fetcher,
    url: string,
    { query, variables, headers }: RequestConfig = {},
  ): Promise<Record<string, any>> => {
    const { data, errors } = await onFetch(url, {
      method: 'POST',
      body: JSON.stringify({
        query,
        variables,
      }),
      headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    });
    if (errors) {
      throw new GraphQLError(errors);
    }
    return data;
  },
);

export const sendAuthorizedRequest = $(
  async (
    onFetch: Fetcher,
    url: string,
    {
      query,
      variables,
      onGetAuthHeader = async () => ({}),
      onUnauthorized = async () => {},
      onInvalidTokens = async () => {},
    }: AuthorizedRequestProps,
  ) => {
    try {
      const headers = await onGetAuthHeader();
      return await sendRequest(onFetch, url, { query, variables, headers });
    } catch (e) {
      if (
        !(e instanceof GraphQLError) ||
        !e.errors.some(error =>
          ['Authentication token required', 'Invalid token'].includes(
            error.message,
          ),
        )
      ) {
        throw e;
      }
      try {
        await onUnauthorized();
      } catch (error) {
        await onInvalidTokens();
      }
      const headers = await onGetAuthHeader();
      return await sendRequest(onFetch, url, { query, variables, headers });
    }
  },
);
