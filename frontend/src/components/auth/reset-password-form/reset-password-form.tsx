import { $, component$, type PropFunction } from '@builder.io/qwik';
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

import { FormBody } from '~/components/common/form-body/form-body';
import { SubmitButton } from '~/components/common/submit-button/submit-button';
import { TextInput } from '~/components/common/text-input/text-input';
import { MIN_PASSWORD_LENGTH } from '~/routes/schema-config';
import { type ResetPasswordInput } from '~/services/graphql';

export type ResetPasswordFormSchema = {
  password: string;
  repeatedPassword: string;
};

interface ResetPasswordFormProps {
  onSubmit$: PropFunction<
    (input: Omit<ResetPasswordInput, 'token'>) => Promise<void>
  >;
}

export const ResetPasswordForm = component$<ResetPasswordFormProps>(
  ({ onSubmit$ }) => {
    const t = inlineTranslate();

    const [form, { Form, Field }] = useForm<ResetPasswordFormSchema>({
      loader: { value: { password: '', repeatedPassword: '' } },
    });

    const handleSubmit = $<SubmitHandler<ResetPasswordFormSchema>>(
      async ({ password }, _event) => {
        const t = inlineTranslate();
        await onSubmit$({ password });
        reset(form);
        setResponse(form, {
          message: t('resetPassword.resetPasswordSuccess'),
        });
      },
    );

    const passwordLabel = t('auth.password');
    const repeatPasswordLabel = t('auth.repeatPassword');

    return (
      <Form onSubmit$={handleSubmit}>
        <FormBody>
          <Field
            name="password"
            validate={[
              // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
              required(t('validation.fieldRequired')),
              minLength(
                MIN_PASSWORD_LENGTH,
                t('validation.passwordTooShort', { min: MIN_PASSWORD_LENGTH }),
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
            name="repeatedPassword"
            validate={[
              // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
              required(t('validation.fieldRequired')),
              // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
              custom$(
                value => value === getValue(form, 'password'),
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
          <div>{form.response.message}</div>
          <SubmitButton submitting={form.submitting}>
            {t('resetPassword.resetPassword')}
          </SubmitButton>
        </FormBody>
      </Form>
    );
  },
);
