interface EnvGetter {
  get: (key: string) => string | undefined;
}

export const getServerGraphQLApiUrl = (env: EnvGetter): string =>
  env.get('SERVER_GRAPHQL_API_URL') ?? 'http://proxy/api/graphql';
