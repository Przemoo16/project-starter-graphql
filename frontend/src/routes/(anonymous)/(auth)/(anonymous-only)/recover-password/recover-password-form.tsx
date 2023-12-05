import { $, component$ } from '@builder.io/qwik';
import {
  email,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { recoverPassword } from '~/services/user/recover-password';

type RecoverPasswordFormSchema = {
  email: string;
};

export const RecoverPasswordForm = component$(() => {
  const t = inlineTranslate();
  const [recoverPasswordForm, { Form, Field }] =
    useForm<RecoverPasswordFormSchema>({
      loader: { value: { email: '' } },
    });

  const handleSubmit = $<SubmitHandler<RecoverPasswordFormSchema>>(
    async (values, _event) => {
      const t = inlineTranslate();

      await recoverPassword(getClientRequestSender(), values.email);

      reset(recoverPasswordForm);
      setResponse(recoverPasswordForm, {
        message: t('recoverPassword.recoverPasswordSuccess'),
      });
    },
  );

  const emailLabel = t('auth.email');

  return (
    <Form onSubmit$={handleSubmit}>
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
      <div>{recoverPasswordForm.response.message}</div>
      <button type="submit" disabled={recoverPasswordForm.submitting}>
        {t('recoverPassword.recoverPassword')}
      </button>
    </Form>
  );
});
