import { $ } from '@builder.io/qwik';

import { RequestError } from './errors';

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
  getAuthHeader?: () => Promise<Record<string, string>>;
  onUnauthorized?: () => Promise<void>;
  onInvalidTokens?: () => Promise<void>;
}

export const sendRequest = $(
  async (
    fetcher: Fetcher,
    url: string,
    { query, variables, headers }: RequestConfig = {},
  ): Promise<Record<string, any>> => {
    const { data, errors } = await fetcher(url, {
      method: 'POST',
      body: JSON.stringify({
        query,
        variables,
      }),
      headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    });
    if (errors) {
      throw new RequestError(errors);
    }
    return data;
  },
);

export const sendAuthorizedRequest = $(
  async (
    fetcher: Fetcher,
    url: string,
    {
      query,
      variables,
      getAuthHeader = async () => ({}),
      onUnauthorized = async () => {},
      onInvalidTokens = async () => {},
    }: AuthorizedRequestProps,
  ) => {
    try {
      const headers = await getAuthHeader();
      return await sendRequest(fetcher, url, { query, variables, headers });
    } catch (e) {
      const error = e as RequestError;
      if (!error.errors.some(error => error.message === 'Invalid token')) {
        throw e;
      }
      try {
        await onUnauthorized();
      } catch (error) {
        await onInvalidTokens();
      }
      const headers = await getAuthHeader();
      return await sendRequest(fetcher, url, { query, variables, headers });
    }
  },
);
