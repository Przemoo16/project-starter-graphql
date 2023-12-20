import {
  GraphQLError,
  type GraphQLErrorDetails,
} from '~/libs/api/graphql-error';

import { type Fetcher } from './types';

export interface RequestConfig {
  query?: string;
  variables?: Record<string, unknown>;
  headers?: Record<string, string>;
}

export const sendGraphQLRequest = async (
  onFetch: Fetcher,
  url: string,
  { query, variables, headers }: RequestConfig = {},
) => {
  const { data, errors } = (await onFetch(url, {
    method: 'POST',
    body: JSON.stringify({
      query,
      variables,
    }),
    headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    withCredentials: false,
  })) as { data: Record<string, unknown>; errors: GraphQLErrorDetails[] };
  if (errors) {
    throw new GraphQLError(errors);
  }
  return data;
};
