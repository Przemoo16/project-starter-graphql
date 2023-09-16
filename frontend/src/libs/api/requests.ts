import { $ } from '@builder.io/qwik';

type Fetcher = (
  url: string,
  method?: string,
  body?: string,
  headers?: Record<string, string>,
) => Promise<any>;

interface ErrorLocation {
  line: number;
  column: number;
}

interface GraphQLError {
  message: string;
  locations: ErrorLocation[];
  path: string[];
}

export class RequestError extends Error {
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

export const getApiURL = $((isServer: boolean): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL ?? 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL ?? 'http://localhost:5173/graphql';
  return isServer ? serverApiURL : clientApiURL;
});

export const fetchAdapter = $(
  async (
    url: string,
    method?: string,
    body?: string,
    headers?: Record<string, string>,
  ) => {
    const response = await fetch(url, {
      method,
      headers,
      body,
    });

    return await response.json();
  },
);

export const sendRequest = $(
  async (
    fetcher: Fetcher,
    url: string,
    query: string,
    variables?: Record<string, unknown>,
    headers?: Record<string, string>,
  ) => {
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
    authHeaderRetriever: () => Promise<Record<string, string>>,
    onUnauthorized: () => Promise<unknown>,
    onInvalidTokens: () => Promise<void>,
    variables?: Record<string, unknown>,
  ) => {
    const authHeader = await authHeaderRetriever();
    const originalRequest = async (): Promise<Record<string, unknown>> =>
      await sendRequest(fetcher, url, query, variables, authHeader);

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
