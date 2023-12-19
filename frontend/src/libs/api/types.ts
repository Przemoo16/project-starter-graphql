export interface FetcherConfig {
  method?: string;
  body?: BodyInit | null;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

export type Fetcher = (
  url: string,
  config: FetcherConfig,
) => Promise<Record<string, unknown>>;
