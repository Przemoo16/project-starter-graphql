import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';
import { routeLoader$ } from '@builder.io/qwik-city';
import {
  custom$,
  getValue,
  type InitialValues,
  minLength,
  required,
  useForm,
} from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MIN_PASSWORD_LENGTH } from '~/constants';

export const head: DocumentHead = {
  title: 'runtime.resetPassword.head.title',
};

export const useFormLoader = routeLoader$<InitialValues<ResetPasswordForm>>(
  () => ({
    password: '',
    repeatPassword: '',
  }),
);

type ResetPasswordForm = {
  password: string;
  repeatPassword: string;
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <ResetPassword />
  </Speak>
));

const ResetPassword = component$(() => {
  const t = useTranslate();
  const [form, { Form, Field }] = useForm<ResetPasswordForm>({
    loader: useFormLoader(),
  });

  const passwordLabel = t('auth.password');
  const repeatPasswordLabel = t('auth.repeatPassword');

  return (
    <Form>
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
            placeholder="********"
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
            value => value === getValue(form, 'password'),
            t(`validation.passwordMatch`),
          ),
        ]}
      >
        {(field, props) => (
          <TextInput
            {...props}
            type="password"
            label={repeatPasswordLabel}
            placeholder="********"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <button type="submit">{t('auth.resetPassword')}</button>
    </Form>
  );
});
