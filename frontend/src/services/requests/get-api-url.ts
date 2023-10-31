export const getApiGraphQLUrl = (isServer: boolean): string => {
  const serverApiURL: string =
    import.meta.env.VITE_SERVER_BACKEND_GRAPHQL_URL ??
    'http://proxy/api/graphql';
  const clientApiURL: string =
    import.meta.env.VITE_CLIENT_BACKEND_GRAPHQL_URL ??
    'http://localhost:5173/api/graphql';
  return isServer ? serverApiURL : clientApiURL;
};
