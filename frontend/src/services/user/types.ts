export type RequestSender = (
  query: string,
  variables?: Record<string, unknown>,
) => Promise<Record<string, any>>;
