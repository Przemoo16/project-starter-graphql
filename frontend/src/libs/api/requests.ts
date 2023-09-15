import { $ } from '@builder.io/qwik';

type RequestSender = (
  url: string,
  query: string,
  variables?: Record<string, unknown>,
  headers?: Record<string, string>,
) => Promise<any>;

export const getApiURL = $((isRunningOnTheServer: boolean): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL ?? 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL ?? 'http://localhost:5173/graphql';
  return isRunningOnTheServer ? serverApiURL : clientApiURL;
});

interface ErrorLocation {
  line: number;
  column: number;
}

interface GraphQLError {
  message: string;
  location: ErrorLocation[];
  path: string;
}

class RequestError extends Error {
  errors: GraphQLError[];

  constructor(
    errors: GraphQLError[],
    message?: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.errors = errors;
    Error.captureStackTrace(this, RequestError);
  }
}

export const sendRequest = $(
  async (
    url: string,
    query: string,
    variables?: Record<string, unknown>,
    headers?: Record<string, string>,
  ) =>
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
      body: JSON.stringify({
        query,
        variables, // TODO: Change if works with undefined
      }),
    }),
);

export const sendRequestWithErrorHandling = $(
  async (
    url: string,
    query: string,
    requestSender: RequestSender,
    variables?: Record<string, unknown>,
    headers?: Record<string, string>,
  ) => {
    const response = await requestSender(url, query, variables, headers);
    const { data, errors } = await response.json();
    if (errors) {
      throw new RequestError(errors);
    }
    return data;
  },
);

export const sendAuthorizedRequest = $(
  async (
    url: string,
    query: string,
    requestSender: RequestSender,
    authHeaderRetriever: () => Promise<Record<string, string>>,
    onUnauthorized: () => Promise<unknown>,
    onInvalidTokens: () => Promise<void>,
    variables?: Record<string, unknown>,
  ) => {
    const authHeader = await authHeaderRetriever();
    const originalRequest = async (): Promise<Record<string, unknown>> =>
      await requestSender(url, query, variables, authHeader);

    try {
      return await originalRequest();
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
      return await originalRequest();
    }
  },
);
