import { GraphQLError } from '~/libs/api/graphql-error';

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

export const sendRequest = async (
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
};
