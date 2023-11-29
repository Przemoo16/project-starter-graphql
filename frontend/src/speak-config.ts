import type { SpeakConfig } from 'qwik-speak';

export const config: SpeakConfig = {
  defaultLocale: {
    lang: 'en-US',
    currency: 'USD',
    timeZone: 'America/Los_Angeles',
  },
  supportedLocales: [
    { lang: 'en-US', currency: 'USD', timeZone: 'America/Los_Angeles' },
  ],
  // Translations available in the whole app
  assets: ['head'],
  // Translations with dynamic keys available in the whole app
  runtimeAssets: [],
};
