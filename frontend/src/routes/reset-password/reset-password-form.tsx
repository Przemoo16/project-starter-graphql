import { $, component$ } from '@builder.io/qwik';
import { useLocation } from '@builder.io/qwik-city';
import {
  custom$,
  FormError,
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
import { MIN_PASSWORD_LENGTH } from '~/routes/schema-config';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { resetPassword } from '~/services/user/reset-password';

type ResetPasswordFormSchema = {
  password: string;
  repeatPassword: string;
};

export const ResetPasswordForm = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const loc = useLocation();
  const [resetPasswordForm, { Form, Field }] = useForm<ResetPasswordFormSchema>(
    {
      loader: { value: { password: '', repeatPassword: '' } },
    },
  );

  const handleSubmit = $<SubmitHandler<ResetPasswordFormSchema>>(
    async (values, _event) => {
      const data = await resetPassword(
        getClientRequestSender(),
        loc.url.searchParams.get('token') ?? '',
        values.password,
      );

      if ('problems' in data) {
        throw new FormError<ResetPasswordFormSchema>(
          inlineTranslate('resetPassword.resetPasswordError', ctx),
        );
      }

      reset(resetPasswordForm);
      setResponse(resetPasswordForm, {
        message: inlineTranslate('resetPassword.resetPasswordSuccess', ctx),
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
        {t('resetPassword.resetPassword')}
      </button>
    </Form>
  );
});
