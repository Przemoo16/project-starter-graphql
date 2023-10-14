import './global.css';

import { component$, useVisibleTask$ } from '@builder.io/qwik';
import {
  QwikCityProvider,
  RouterOutlet,
  ServiceWorkerRegister,
} from '@builder.io/qwik-city';
import { QwikSpeakProvider } from 'qwik-speak';

import { RouterHead } from './components/router-head/router-head';
import { BrowserStorage } from './libs/storage/browser-storage';
import { getClientRequestSender } from './services/requests/get-client-request-sender';
import { getClientTokenStorage } from './services/tokens/get-client-token-storage';
import { checkTokenValidity } from './services/user/check-token-validity';
import { getMe } from './services/user/get-me';
import { config } from './speak-config';
import { translationFn } from './speak-functions';

export default component$(() => {
  /**
   * The root of a QwikCity site always start with the <QwikCityProvider> component,
   * immediately followed by the document's <head> and <body>.
   *
   * Don't remove the `<head>` and `<body>` elements.
   */

  // TODO: Ideally it this done on the server before rendering component, however
  // I couldn't find the way to execute it only once on page enter.
  useVisibleTask$(async () => {
    await checkTokenValidity(new BrowserStorage(sessionStorage), async () => {
      await getMe(getClientRequestSender(), getClientTokenStorage());
    });
  });

  return (
    <QwikSpeakProvider config={config} translationFn={translationFn}>
      <QwikCityProvider>
        <head>
          <meta charSet="utf-8" />
          <link rel="manifest" href="/manifest.json" />
          <RouterHead />
          <ServiceWorkerRegister />
        </head>
        <body lang="en">
          <RouterOutlet />
        </body>
      </QwikCityProvider>
    </QwikSpeakProvider>
  );
});
