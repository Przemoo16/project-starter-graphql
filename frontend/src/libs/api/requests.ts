import { $ } from '@builder.io/qwik';

import { RequestError } from './errors';

export type Fetcher = (
  url: string,
  method?: string,
  body?: string,
  headers?: Record<string, string>,
) => Promise<Record<string, any>>;

export const sendRequest = $(
  async (
    fetcher: Fetcher,
    url: string,
    query: string,
    variables?: Record<string, unknown>,
    headers?: Record<string, string>,
  ): Promise<Record<string, any>> => {
    const { data, errors } = await fetcher(
      url,
      'POST',
      JSON.stringify({
        query,
        variables,
      }),
      { 'Content-Type': 'application/json', ...(headers ?? {}) },
    );
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
    query: string,
    variables?: Record<string, unknown>,
    getAuthHeader: () => Promise<Record<string, string>> = async () => ({}),
    onUnauthorized: () => Promise<void> = async () => {},
    onInvalidTokens: () => Promise<void> = async () => {},
  ) => {
    try {
      const authHeader = await getAuthHeader();
      return await sendRequest(fetcher, url, query, variables, authHeader);
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
      const authHeader = await getAuthHeader();
      return await sendRequest(fetcher, url, query, variables, authHeader);
    }
  },
);
