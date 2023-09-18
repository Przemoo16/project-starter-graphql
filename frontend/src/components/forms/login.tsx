import { component$, type QRL } from '@builder.io/qwik';
import {
  email,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

export type LoginFormSchema = {
  email: string;
  password: string;
};

interface LoginFormProps {
  onSubmit: QRL<SubmitHandler<LoginFormSchema>>;
}

export const LoginForm = component$(({ onSubmit }: LoginFormProps) => {
  const t = useTranslate();
  const [loginForm, { Form, Field }] = useForm<LoginFormSchema>({
    loader: { value: { email: '', password: '' } },
  });

  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');

  return (
    <Form onSubmit$={onSubmit}>
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
      <div>{loginForm.response.message}</div>
      <button type="submit" disabled={loginForm.submitting}>
        {t('auth.loginButton')}
      </button>
    </Form>
  );
});
