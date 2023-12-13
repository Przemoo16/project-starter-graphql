import { $, component$, type QRL } from '@builder.io/qwik';
import {
  email,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

export type LoginFormSchema = {
  email: string;
  password: string;
};

interface LoginFormProps {
  onSubmit: QRL<(email: string, fullName: string) => Promise<void>>;
}

export const LoginForm = component$(({ onSubmit }: LoginFormProps) => {
  const t = inlineTranslate();
  const [loginForm, { Form, Field }] = useForm<LoginFormSchema>({
    loader: { value: { email: '', password: '' } },
  });

  const handleSubmit = $<SubmitHandler<LoginFormSchema>>(
    async ({ email, password }, _event) => {
      await onSubmit(email, password);
    },
  );

  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');

  return (
    <Form onSubmit$={handleSubmit}>
      <Field
        name="email"
        validate={[
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
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
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          required(t('validation.required')),
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
      <div>{loginForm.response.message}</div>
      <button type="submit" disabled={loginForm.submitting}>
        {t('login.login')}
      </button>
    </Form>
  );
});
