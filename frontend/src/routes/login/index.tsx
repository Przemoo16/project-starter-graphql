import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestEvent,
} from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/urls';
import { onOnlyAnonymousRoute } from '~/services/auth';

import { LoginForm } from './login-form';

export const head: DocumentHead = {
  title: 'runtime.login.head.title',
};

export const onRequest = async (requestEvent: RequestEvent) => {
  await onOnlyAnonymousRoute(requestEvent);
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Login />
  </Speak>
));

const Login = component$(() => {
  const t = useTranslate();

  return (
    <>
      <LoginForm />
      <Link href={RouteURL.Register}>{t('auth.registerLink')}</Link>
      <Link href={RouteURL.RecoverPassword}>
        {t('auth.recoverPasswordLink')}
      </Link>
    </>
  );
});
