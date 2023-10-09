import { GraphQLError } from '~/libs/api/graphql-error';

import { type RequestConfig, sendGraphQLRequest } from './send-graphql-request';
import { type Fetcher } from './types';

interface AuthorizedRequestProps extends Omit<RequestConfig, 'headers'> {
  onGetAuthHeader?: () => Record<string, string>;
  onUnauthorized?: () => Promise<void>;
  onInvalidTokens?: () => void;
}

export const sendGraphQLAuthorizedRequest = async (
  onFetch: Fetcher,
  url: string,
  {
    query,
    variables,
    onGetAuthHeader = () => ({}),
    onUnauthorized = async () => {},
    onInvalidTokens = () => {},
  }: AuthorizedRequestProps,
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
      onInvalidTokens();
    }
    const headers = onGetAuthHeader();
    return await sendGraphQLRequest(onFetch, url, {
      query,
      variables,
      headers,
    });
  }
};
