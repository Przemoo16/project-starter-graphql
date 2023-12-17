import type { RequestHandler } from '@builder.io/qwik-city';

import { config } from '~/speak-config';

export const onRequest: RequestHandler = ({ locale }) => {
  locale(config.defaultLocale.lang);
};
