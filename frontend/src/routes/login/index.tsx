import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, Link, useNavigate } from '@builder.io/qwik-city';
import { FormError, type SubmitHandler } from '@modular-forms/qwik';
import {
  inlineTranslate,
  Speak,
  useSpeakContext,
  useTranslate,
} from 'qwik-speak';

import { LoginForm, type LoginFormSchema } from '~/components/forms/login';
import { isProblemPresent } from '~/libs/api/errors';
import { getTokenStorage, REQUEST_SENDER } from '~/services/context';
import { login } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.login.head.title',
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Login />
  </Speak>
));

const Login = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const nav = useNavigate();

  const handleSubmit = $<SubmitHandler<LoginFormSchema>>(
    async (values, _event) => {
      const { problems } = await login(
        REQUEST_SENDER,
        await getTokenStorage(),
        values.email,
        values.password,
      );

      if (problems) {
        let error = '';
        if (isProblemPresent(problems, 'UserEmailNotConfirmedProblem')) {
          error = inlineTranslate('auth.accountEmailNotConfirmed', ctx);
        } else {
          error = inlineTranslate('auth.invalidCredentials', ctx);
        }
        throw new FormError<LoginFormSchema>(error);
      }

      await nav('/dashboard');
    },
  );

  return (
    <>
      <LoginForm onSubmit={handleSubmit} />
      <Link href="/register">{t('auth.registerLink')}</Link>
      <Link href="/recover-password">{t('auth.recoverPasswordLink')}</Link>
    </>
  );
});
