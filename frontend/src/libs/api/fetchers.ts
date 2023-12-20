import { type FetcherConfig } from './types';

export const fetchAdapter = async (
  url: string,
  config: FetcherConfig,
): Promise<Record<string, unknown>> => {
  const response = await fetch(url, {
    method: config.method,
    body: config.body,
    headers: config.headers,
    credentials: config.withCredentials ? 'include' : 'omit',
  });
  return await response.json();
};
