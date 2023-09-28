import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestEvent,
} from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/urls';
import { onOnlyAnonymousRoute } from '~/services/auth';

import { RegisterForm } from './register-form';

export const head: DocumentHead = {
  title: 'runtime.register.head.title',
};

export const onRequest = (requestEvent: RequestEvent) => {
  onOnlyAnonymousRoute(requestEvent);
};

export default component$(() => (
  <Speak assets={['account', 'auth', 'register', 'validation']}>
    <Register />
  </Speak>
));

const Register = component$(() => {
  const t = useTranslate();

  return (
    <>
      <RegisterForm />
      <Link href={RouteURL.Login}>{t('register.doHaveAccount')}</Link>
    </>
  );
});
