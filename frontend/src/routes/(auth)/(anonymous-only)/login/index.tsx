import { $, component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  useLocation,
  useNavigate,
} from '@builder.io/qwik-city';
import { FormError } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import { getClientTokenStorage } from '~/auth/get-client-token-storage';
import { FormLink } from '~/components/auth/form-link/form-link';
import { FormTitle } from '~/components/auth/form-title/form-title';
import { LinksContainer } from '~/components/auth/links-container/links-container';
import {
  LoginForm,
  type LoginFormSchema,
} from '~/components/login-form/login-form';
import { hasProblems } from '~/libs/api/has-problems';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { RouteURL } from '~/libs/api/route-url';
import { type LoginInput } from '~/services/graphql';
import { login } from '~/services/user/login';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.login.title'),
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

  const onSubmit = $(async (input: LoginInput) => {
    const t = inlineTranslate();

    const data = await login(
      getClientRequestSender(),
      getClientTokenStorage(),
      input,
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
      <FormTitle>{t('login.signInToYourAccount')}</FormTitle>
      <LoginForm onSubmit={onSubmit} />
      <LinksContainer>
        <FormLink href={RouteURL.Register}>
          {t('login.doNotHaveAccount')}
        </FormLink>
        <FormLink href={RouteURL.RecoverPassword}>
          {t('login.forgotPassword')}
        </FormLink>
      </LinksContainer>
    </>
  );
});
