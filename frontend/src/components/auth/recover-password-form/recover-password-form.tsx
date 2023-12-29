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

import { SubmitButton } from '~/components/auth/submit-button/submit-button';
import { TextInput } from '~/components/common/text-input/text-input';

import { FormBody } from '../form-body/form-body';

type RecoverPasswordFormSchema = {
  email: string;
};

interface RecoverPasswordFormProps {
  onSubmit: QRL<(email: string) => Promise<void>>;
}

export const RecoverPasswordForm = component$<RecoverPasswordFormProps>(
  ({ onSubmit }) => {
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
          <div>{form.response.message}</div>
          <SubmitButton submitting={form.submitting}>
            {t('recoverPassword.recoverPassword')}
          </SubmitButton>
        </FormBody>
      </Form>
    );
  },
);
