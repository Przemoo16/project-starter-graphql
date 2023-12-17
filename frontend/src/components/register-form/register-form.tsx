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
  repeatedPassword: string;
};

interface RegisterFormProps {
  onSubmit: QRL<
    (fullName: string, email: string, password: string) => Promise<void>
  >;
}

export const RegisterForm = component$(({ onSubmit }: RegisterFormProps) => {
  const t = inlineTranslate();
  const [form, { Form, Field }] = useForm<RegisterFormSchema>({
    loader: {
      value: { fullName: '', email: '', password: '', repeatedPassword: '' },
    },
  });

  const handleSubmit = $<SubmitHandler<RegisterFormSchema>>(
    async ({ fullName, email, password }, _event) => {
      const t = inlineTranslate();
      await onSubmit(fullName, email, password);
      reset(form);
      setResponse(form, {
        message: t('register.registerSuccess'),
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
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          required(t('validation.fieldRequired')),
          maxLength(
            MAX_FULL_NAME_LENGTH,
            t('validation.fullNameTooLong', { max: MAX_FULL_NAME_LENGTH }),
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
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          required(t('validation.fieldRequired')),
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
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          required(t('validation.fieldRequired')),
          minLength(
            MIN_PASSWORD_LENGTH,
            t('validation.passwordTooShort', { min: MIN_PASSWORD_LENGTH }),
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
        name="repeatedPassword"
        validate={[
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          required(t('validation.fieldRequired')),
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          custom$(
            value => value === getValue(form, 'password'),
            t(`validation.passwordDoesNotMatch`),
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
      <div>{form.response.message}</div>
      <button type="submit" disabled={form.submitting}>
        {t('register.getStarted')}
      </button>
    </Form>
  );
});
