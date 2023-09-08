import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';
import { routeLoader$ } from '@builder.io/qwik-city';
import {
  email,
  type InitialValues,
  required,
  useForm,
} from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

export const head: DocumentHead = {
  title: 'runtime.login.head.title',
};

type LoginForm = {
  email: string;
  password: string;
};

export const useFormLoader = routeLoader$<InitialValues<LoginForm>>(() => ({
  email: '',
  password: '',
}));

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Login />
  </Speak>
));

const Login = component$(() => {
  const t = useTranslate();
  const [, { Form, Field }] = useForm<LoginForm>({
    loader: useFormLoader(),
  });

  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');

  return (
    <Form>
      <Field
        name="email"
        validate={[
          required(t('validation.required')),
          email(t('validation.invalidEmail')),
        ]}
      >
        {(field, props) => (
          <TextInput
            {...props}
            type="email"
            label={emailLabel}
            placeholder="joe@example.com"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <Field name="password" validate={[required(t('validation.required'))]}>
        {(field, props) => (
          <TextInput
            {...props}
            type="password"
            label={passwordLabel}
            placeholder="********"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <button type="submit">{t('auth.loginButton')}</button>
    </Form>
  );
});
