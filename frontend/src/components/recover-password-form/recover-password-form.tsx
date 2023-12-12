import { $, component$, type QRL } from '@builder.io/qwik';
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

type RecoverPasswordFormSchema = {
  email: string;
};

interface RecoverPasswordFormProps {
  onSubmit: QRL<(email: string) => Promise<string>>;
}

export const RecoverPasswordForm = component$(
  ({ onSubmit }: RecoverPasswordFormProps) => {
    const t = inlineTranslate();
    const [recoverPasswordForm, { Form, Field }] =
      useForm<RecoverPasswordFormSchema>({
        loader: { value: { email: '' } },
      });

    const handleSubmit = $<SubmitHandler<RecoverPasswordFormSchema>>(
      async ({ email }, _event) => {
        const message = await onSubmit(email);
        reset(recoverPasswordForm);
        setResponse(recoverPasswordForm, {
          message,
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
  },
);