import { $, component$, type QRL } from '@builder.io/qwik';
import {
  custom$,
  email,
  getValue,
  maxLength,
  minLength,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import {
  MAX_FULL_NAME_LENGTH,
  MIN_PASSWORD_LENGTH,
} from '~/routes/schema-config';

export type RegisterFormSchema = {
  fullName: string;
  email: string;
  password: string;
  repeatPassword: string;
};

interface RegisterFormProps {
  onSubmit: QRL<
    (fullName: string, email: string, password: string) => Promise<string>
  >;
}

export const RegisterForm = component$(({ onSubmit }: RegisterFormProps) => {
  const t = inlineTranslate();
  const [registerForm, { Form, Field }] = useForm<RegisterFormSchema>({
    loader: {
      value: { fullName: '', email: '', password: '', repeatPassword: '' },
    },
  });

  const handleSubmit = $<SubmitHandler<RegisterFormSchema>>(
    async ({ fullName, email, password }, _event) => {
      const message = await onSubmit(fullName, email, password);
      reset(registerForm);
      setResponse(registerForm, {
        message,
      });
    },
  );

  const fullNameLabel = t('account.fullName');
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
            placeholder="joe@example.com"
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
            placeholder="********"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <div>{registerForm.response.message}</div>
      <button type="submit" disabled={registerForm.submitting}>
        {t('register.getStarted')}
      </button>
    </Form>
  );
});
