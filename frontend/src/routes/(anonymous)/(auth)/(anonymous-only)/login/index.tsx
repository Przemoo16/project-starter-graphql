import { $, component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  useLocation,
  useNavigate,
} from '@builder.io/qwik-city';
import { FormError } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import {
  LoginForm,
  type LoginFormSchema,
} from '~/components/login-form/login-form';
import { hasProblems } from '~/libs/api/has-problems';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { RouteURL } from '~/libs/api/route-url';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { getClientTokenStorage } from '~/services/tokens/get-client-token-storage';
import { login } from '~/services/user/login';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.login.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'login', 'validation'] });

  return <Login />;
});

const Login = component$(() => {
  const t = inlineTranslate();
  const nav = useNavigate();
  const loc = useLocation();

  const onSubmit = $(async (email: string, password: string) => {
    const t = inlineTranslate();

    const data = await login(
      getClientRequestSender(),
      getClientTokenStorage(),
      email,
      password,
    );

    if (hasProblems(data)) {
      let error = '';
      if (isProblemPresent(data.problems, 'UserEmailNotConfirmedProblem')) {
        error = t('login.emailNotConfirmed');
      } else {
        error = t('login.invalidCredentials');
      }
      throw new FormError<LoginFormSchema>(error);
    }

    await nav(loc.url.searchParams.get('callbackUrl') ?? RouteURL.Dashboard);
  });

  return (
    <>
      <LoginForm onSubmit={onSubmit} />
      <Link href={RouteURL.Register}>{t('login.doNotHaveAccount')}</Link>
      <Link href={RouteURL.RecoverPassword}>{t('login.forgotPassword')}</Link>
    </>
  );
});
