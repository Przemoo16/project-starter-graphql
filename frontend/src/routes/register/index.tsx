import { $, component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';
import { routeLoader$ } from '@builder.io/qwik-city';
import {
  custom$,
  email,
  getValue,
  type InitialValues,
  maxLength,
  minLength,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

const MAX_FULL_NAME_LENGTH = 128;
const MIN_PASSWORD_LENGTH = 8;

export const head: DocumentHead = {
  title: 'runtime.register.head.title',
};

type RegisterForm = {
  fullName: string;
  email: string;
  password: string;
  repeatPassword: string;
};

export const useFormLoader = routeLoader$<InitialValues<RegisterForm>>(() => ({
  fullName: '',
  email: '',
  password: '',
  repeatPassword: '',
}));

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Register />
  </Speak>
));

const Register = component$(() => {
  const t = useTranslate();
  const [registerForm, { Form, Field }] = useForm<RegisterForm>({
    loader: useFormLoader(),
  });

  const handleSubmit = $<SubmitHandler<RegisterForm>>((values, event) => {
    // Runs on client
    console.log(values);
  });

  const fullNameLabel = t('auth.fullName');
  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');
  const repeatPasswordLabel = t('auth.repeatPassword');

  return (
    <Form onSubmit$={handleSubmit}>
      <Field
        name="fullName"
        validate={[
          required(t('validation.required')),
          maxLength(
            MAX_FULL_NAME_LENGTH,
            t('validation.maxFullName', { max: MAX_FULL_NAME_LENGTH }),
          ),
        ]}
      >
        {(field, props) => (
          <TextInput
            {...props}
            type="text"
            label={fullNameLabel}
            placeholder="Jon Doe"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
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
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <Field
        name="password"
        validate={[
          required(t('validation.required')),
          minLength(
            MIN_PASSWORD_LENGTH,
            t('validation.minPassword', { min: MIN_PASSWORD_LENGTH }),
          ),
        ]}
      >
        {(field, props) => (
          <TextInput
            {...props}
            type="password"
            label={passwordLabel}
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <Field
        name="repeatPassword"
        validate={[
          required(t('validation.required')),
          custom$(
            value => value === getValue(registerForm, 'password'),
            t(`validation.passwordMatch`),
          ),
        ]}
      >
        {(field, props) => (
          <TextInput
            {...props}
            type="password"
            label={repeatPasswordLabel}
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <button type="submit">{t('auth.getStarted')}</button>
    </Form>
  );
});
