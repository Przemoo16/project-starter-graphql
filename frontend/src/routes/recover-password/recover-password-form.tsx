import { $, component$ } from '@builder.io/qwik';
import {
  email,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate, useSpeakContext, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { REQUEST_SENDER } from '~/services/context';
import { recoverPassword } from '~/services/user';

type RecoverPasswordFormSchema = {
  email: string;
};

export const RecoverPasswordForm = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const [recoverPasswordForm, { Form, Field }] =
    useForm<RecoverPasswordFormSchema>({
      loader: { value: { email: '' } },
    });

  const handleSubmit = $<SubmitHandler<RecoverPasswordFormSchema>>(
    async (values, _event) => {
      await recoverPassword(REQUEST_SENDER, values.email);

      reset(recoverPasswordForm);
      setResponse(recoverPasswordForm, {
        message: inlineTranslate('auth.recoverPasswordSuccess', ctx),
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
        {t('auth.recoverPassword')}
      </button>
    </Form>
  );
});
