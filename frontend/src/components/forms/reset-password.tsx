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
import { inlineTranslate, useSpeakContext, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

import { MIN_PASSWORD_LENGTH } from './schema-config';

export type ResetPasswordFormSchema = {
  password: string;
  repeatPassword: string;
};

interface ResetPasswordFormProps {
  onSubmit: QRL<SubmitHandler<ResetPasswordFormSchema>>;
}

export const ResetPasswordForm = component$(
  ({ onSubmit }: ResetPasswordFormProps) => {
    const t = useTranslate();
    const ctx = useSpeakContext();
    const [resetPasswordForm, { Form, Field }] =
      useForm<ResetPasswordFormSchema>({
        loader: { value: { password: '', repeatPassword: '' } },
      });

    const passwordLabel = t('auth.password');
    const repeatPasswordLabel = t('auth.repeatPassword');

    const handleSubmit = $<SubmitHandler<ResetPasswordFormSchema>>(
      async (values, event) => {
        await onSubmit(values, event);

        reset(resetPasswordForm);
        setResponse(resetPasswordForm, {
          message: inlineTranslate('auth.resetPasswordSuccess', ctx),
        });
      },
    );

    return (
      <Form onSubmit$={handleSubmit}>
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
              value => value === getValue(resetPasswordForm, 'password'),
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
        <div>{resetPasswordForm.response.message}</div>
        <button type="submit" disabled={resetPasswordForm.submitting}>
          {t('auth.resetPassword')}
        </button>
      </Form>
    );
  },
);
