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

import { LoadingButton } from '../loading-button/loading-button';

type RecoverPasswordFormSchema = {
  email: string;
};

interface RecoverPasswordFormProps {
  onSubmit: QRL<(email: string) => Promise<void>>;
}

export const RecoverPasswordForm = component$(
  ({ onSubmit }: RecoverPasswordFormProps) => {
    const t = inlineTranslate();
    const [form, { Form, Field }] = useForm<RecoverPasswordFormSchema>({
      loader: { value: { email: '' } },
    });

    const handleSubmit = $<SubmitHandler<RecoverPasswordFormSchema>>(
      async ({ email }, _event) => {
        const t = inlineTranslate();
        await onSubmit(email);
        reset(form);
        setResponse(form, {
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
        <div>{form.response.message}</div>
        <div class="mt-6 flex flex-col">
          <LoadingButton type="submit" loading={form.submitting}>
            {t('recoverPassword.recoverPassword')}
          </LoadingButton>
        </div>
      </Form>
    );
  },
);
