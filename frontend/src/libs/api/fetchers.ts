import { $ } from '@builder.io/qwik';

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
