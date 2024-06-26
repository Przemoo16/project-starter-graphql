import { $, component$, type PropFunction } from '@builder.io/qwik';
import {
  email,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { FormBody } from '~/components/common/form-body/form-body';
import { SubmitButton } from '~/components/common/submit-button/submit-button';
import { TextInput } from '~/components/common/text-input/text-input';
import { type LoginInput } from '~/services/graphql';

export type LoginFormSchema = {
  email: string;
  password: string;
};

interface LoginFormProps {
  onSubmit$: PropFunction<(input: LoginInput) => Promise<void>>;
}

export const LoginForm = component$<LoginFormProps>(({ onSubmit$ }) => {
  const t = inlineTranslate();
  const [form, { Form, Field }] = useForm<LoginFormSchema>({
    loader: { value: { email: '', password: '' } },
  });

  const handleSubmit = $<SubmitHandler<LoginFormSchema>>(
    async ({ email, password }, _event) => {
      await onSubmit$({ username: email, password });
    },
  );

  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');

  return (
    <Form onSubmit$={handleSubmit}>
      <FormBody>
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
        <div>{form.response.message}</div>
        <SubmitButton submitting={form.submitting}>
          {t('login.signIn')}
        </SubmitButton>
      </FormBody>
    </Form>
  );
});
