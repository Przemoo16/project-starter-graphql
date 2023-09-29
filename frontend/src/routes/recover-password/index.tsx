import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestEvent,
} from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';
import { onOnlyAnonymousRoute } from '~/services/auth/on-only-anonymous-route';

import { RecoverPasswordForm } from './recover-password-form';

export const head: DocumentHead = {
  title: 'runtime.recoverPassword.head.title',
};

export const onRequest = (requestEvent: RequestEvent) => {
  onOnlyAnonymousRoute(requestEvent);
};

export default component$(() => (
  <Speak assets={['auth', 'recoverPassword', 'validation']}>
    <RecoverPassword />
  </Speak>
));

const RecoverPassword = component$(() => {
  const t = useTranslate();

  return (
    <>
      <RecoverPasswordForm />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
