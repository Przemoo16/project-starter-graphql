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
    const [form, { Form, Field }] = useForm<RecoverPasswordFormSchema>({
      loader: { value: { email: '' } },
    });

    const handleSubmit = $<SubmitHandler<RecoverPasswordFormSchema>>(
      async ({ email }, _event) => {
        const message = await onSubmit(email);
        reset(form);
        setResponse(form, {
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
        <div>{form.response.message}</div>
        <button type="submit" disabled={form.submitting}>
          {t('recoverPassword.recoverPassword')}
        </button>
      </Form>
    );
  },
);
