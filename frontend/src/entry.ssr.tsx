/**
 * WHAT IS THIS FILE?
 *
 * SSR entry point, in all cases the application is rendered outside the browser, this
 * entry point will be the common one.
 *
 * - Server (express, cloudflare...)
 * - npm run start
 * - npm run preview
 * - npm run build
 *
 */
import { isDev } from '@builder.io/qwik/build';
import {
  renderToStream,
  type RenderOptions,
  type RenderToStreamOptions,
} from '@builder.io/qwik/server';
import { manifest } from '@qwik-client-manifest';

import Root from './root';
import { config } from './speak-config';

const extractBase = ({ serverData }: RenderOptions) =>
  !isDev && serverData?.locale ? `/build/${serverData.locale}` : '/build';

export default function (opts: RenderToStreamOptions) {
  return renderToStream(<Root />, {
    manifest,
    ...opts,
    base: extractBase,
    containerAttributes: {
      lang: opts.serverData?.locale || config.defaultLocale.lang,
      ...opts.containerAttributes,
    },
  });
}
