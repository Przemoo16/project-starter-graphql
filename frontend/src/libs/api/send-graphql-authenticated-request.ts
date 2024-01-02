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
  const sendRequest = async (headers: Record<string, string>) =>
    await sendGraphQLRequest(onFetch, url, {
      query,
      variables,
      headers,
    });
  const initialHeaders = onGetAuthHeader();

  try {
    return await sendRequest(initialHeaders);
  } catch (initialError) {
    if (!isUnauthorized(initialError)) {
      throw initialError;
    }
    try {
      await onUnauthorized();
    } catch {
      await onInvalidTokens();
    }

    const retryHeaders = onGetAuthHeader();
    try {
      return await sendRequest(retryHeaders);
    } catch (retryError) {
      // Check if despite the refresh token went successfully, there are still token
      // related errors e.g. user has been deleted
      if (isUnauthorized(retryError)) {
        await onInvalidTokens();
      }
      throw retryError;
    }
  }
};

const isUnauthorized = (error: unknown) =>
  error instanceof GraphQLError &&
  error.errors.some(error =>
    ['Authentication token required', 'Invalid token'].includes(error.message),
  );
