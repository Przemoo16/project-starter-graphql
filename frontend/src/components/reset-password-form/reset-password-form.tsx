import { $, component$, type QRL } from '@builder.io/qwik';
import {
  custom$,
  getValue,
  minLength,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MIN_PASSWORD_LENGTH } from '~/routes/schema-config';

export type ResetPasswordFormSchema = {
  password: string;
  repeatPassword: string;
};

interface ResetPasswordFormProps {
  onSubmit: QRL<(password: string) => Promise<string>>;
}

export const ResetPasswordForm = component$(
  ({ onSubmit }: ResetPasswordFormProps) => {
    const t = inlineTranslate();

    const [resetPasswordForm, { Form, Field }] =
      useForm<ResetPasswordFormSchema>({
        loader: { value: { password: '', repeatPassword: '' } },
      });

    const handleSubmit = $<SubmitHandler<ResetPasswordFormSchema>>(
      async ({ password }, _event) => {
        const message = await onSubmit(password);
        reset(resetPasswordForm);
        setResponse(resetPasswordForm, {
          message,
        });
      },
    );

    const passwordLabel = t('auth.password');
    const repeatPasswordLabel = t('auth.repeatPassword');

    return (
      <Form onSubmit$={handleSubmit}>
        <Field
          name="password"
          validate={[
            // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
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
            // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
            required(t('validation.required')),
            // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
            custom$(
              value => value === getValue(resetPasswordForm, 'password'),
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
        <div>{resetPasswordForm.response.message}</div>
        <button type="submit" disabled={resetPasswordForm.submitting}>
          {t('resetPassword.resetPassword')}
        </button>
      </Form>
    );
  },
);
