export const fetchAdapter = async (
  url: string,
  config: RequestInit,
): Promise<Record<string, any>> => {
  const response = await fetch(url, { credentials: 'omit', ...config });
  return await response.json();
};
