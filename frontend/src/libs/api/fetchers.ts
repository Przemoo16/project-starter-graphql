import { $ } from '@builder.io/qwik';

export const fetchAdapter = $(
  async (url: string, config: RequestInit): Promise<Record<string, any>> => {
    const response = await fetch(url, config);
    return await response.json();
  },
);
