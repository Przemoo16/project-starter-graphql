import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { FormError } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import {
  RegisterForm,
  type RegisterFormSchema,
} from '~/components/register-form/register-form';
import { hasProblems } from '~/libs/api/has-problems';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { RouteURL } from '~/libs/api/route-url';
import { type UserCreateInput } from '~/services/graphql';
import { createUser } from '~/services/user/create-user';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.register.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['account', 'auth', 'register', 'validation'] });

  return <Register />;
});

const Register = component$(() => {
  const t = inlineTranslate();

  const onSubmit = $(async (input: UserCreateInput) => {
    const t = inlineTranslate();

    const data = await createUser(getClientRequestSender(), input);

    if (hasProblems(data)) {
      let emailError = '';
      let generalError = '';
      if (isProblemPresent(data.problems, 'UserAlreadyExistsProblem')) {
        emailError = t('register.accountAlreadyExists');
      } else {
        generalError = t('register.registerError');
      }
      throw new FormError<RegisterFormSchema>(generalError, {
        email: emailError,
      });
    }
  });

  return (
    <>
      <RegisterForm onSubmit={onSubmit} />
      <Link href={RouteURL.Login}>{t('register.doHaveAccount')}</Link>
    </>
  );
});
