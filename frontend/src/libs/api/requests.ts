export const sendGraphQLRequest = async (
  url: string,
  query: string,
  variables: Record<string, unknown>,
  headers: Record<string, string> | null = null,
): Promise<Response> =>
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    body: JSON.stringify({
      query,
      variables,
    }),
  });
