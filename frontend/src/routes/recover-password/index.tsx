import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestHandler,
} from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';
import { onOnlyAnonymousRoute } from '~/services/auth/on-only-anonymous-route';

import { RecoverPasswordForm } from './recover-password-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.recoverPassword.title'),
  };
};

export const onRequest: RequestHandler = requestEvent => {
  onOnlyAnonymousRoute(requestEvent);
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'recoverPassword', 'validation'] });

  return <RecoverPassword />;
});

const RecoverPassword = component$(() => {
  const t = inlineTranslate();

  return (
    <>
      <RecoverPasswordForm />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
