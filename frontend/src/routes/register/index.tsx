import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { FormError, type SubmitHandler } from '@modular-forms/qwik';
import { inlineTranslate, Speak, useSpeakContext } from 'qwik-speak';

import {
  RegisterForm,
  type RegisterFormSchema,
} from '~/components/forms/register';
import { isProblemPresent } from '~/libs/api/errors';
import { REQUEST_SENDER } from '~/services/context';
import { register } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.register.head.title',
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Register />
  </Speak>
));

const Register = component$(() => {
  const ctx = useSpeakContext();

  const handleSubmit = $<SubmitHandler<RegisterFormSchema>>(
    async (values, _event) => {
      const { problems } = await register(
        REQUEST_SENDER,
        values.fullName,
        values.email,
        values.password,
      );

      if (problems) {
        let emailError = '';
        let generalError = '';
        if (isProblemPresent(problems, 'UserAlreadyExistsProblem')) {
          emailError = inlineTranslate('auth.accountAlreadyExists', ctx);
        } else {
          generalError = inlineTranslate('auth.registerError', ctx);
        }
        throw new FormError<RegisterFormSchema>(generalError, {
          email: emailError,
        });
      }
    },
  );

  return <RegisterForm onSubmit={handleSubmit} />;
});
