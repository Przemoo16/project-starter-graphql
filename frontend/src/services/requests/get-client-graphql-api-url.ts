export const getClientGraphQLApiUrl = (): string =>
  import.meta.env.PUBLIC_CLIENT_GRAPHQL_API_URL ?? '/api/graphql';
