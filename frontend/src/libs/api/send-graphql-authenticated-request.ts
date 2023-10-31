import { GraphQLError } from '~/libs/api/graphql-error';

import { type RequestConfig, sendGraphQLRequest } from './send-graphql-request';
import { type Fetcher } from './types';

interface AuthenticatedRequestProps extends Omit<RequestConfig, 'headers'> {
  onGetAuthHeader?: () => Record<string, string>;
  onUnauthorized?: () => Promise<unknown>;
  onInvalidTokens?: () => Promise<unknown>;
}

export const sendGraphQLAuthenticatedRequest = async (
  onFetch: Fetcher,
  url: string,
  {
    query,
    variables,
    onGetAuthHeader = () => ({}),
    onUnauthorized = async () => {},
    onInvalidTokens = async () => {},
  }: AuthenticatedRequestProps,
) => {
  try {
    const headers = onGetAuthHeader();
    return await sendGraphQLRequest(onFetch, url, {
      query,
      variables,
      headers,
    });
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
    const headers = onGetAuthHeader();
    return await sendGraphQLRequest(onFetch, url, {
      query,
      variables,
      headers,
    });
  }
};
