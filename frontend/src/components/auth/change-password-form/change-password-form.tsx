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

import { LoadingButton } from '~/components/common/loading-button/loading-button';
import { TextInput } from '~/components/common/text-input/text-input';
import { MIN_PASSWORD_LENGTH } from '~/routes/schema-config';
import { type ChangeMyPasswordInput } from '~/services/graphql';

export type ChangePasswordFormSchema = {
  currentPassword: string;
  newPassword: string;
  repeatedPassword: string;
};

interface ChangePasswordFormProps {
  onSubmit: QRL<(input: ChangeMyPasswordInput) => Promise<void>>;
}

export const ChangePasswordForm = component$(
  ({ onSubmit }: ChangePasswordFormProps) => {
    const t = inlineTranslate();
    const [form, { Form, Field }] = useForm<ChangePasswordFormSchema>({
      loader: {
        value: {
          currentPassword: '',
          newPassword: '',
          repeatedPassword: '',
        },
      },
    });

    const handleSubmit = $<SubmitHandler<ChangePasswordFormSchema>>(
      async ({ currentPassword, newPassword }, _event) => {
        const t = inlineTranslate();
        await onSubmit({ currentPassword, newPassword });
        reset(form);
        setResponse(form, {
          message: t('changePassword.changePasswordSuccess'),
        });
      },
    );

    const currentPasswordLabel = t('changePassword.currentPassword');
    const newPasswordLabel = t('changePassword.newPassword');
    const repeatPasswordLabel = t('auth.repeatPassword');

    return (
      <Form onSubmit$={handleSubmit}>
        <Field
          name="currentPassword"
          // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
          validate={[required(t('validation.fieldRequired'))]}
        >
          {(field, props) => (
            <TextInput
              {...props}
              type="password"
              label={currentPasswordLabel}
              placeholder="********"
              value={field.value}
              error={field.error}
              required
            />
          )}
        </Field>
        <Field
          name="newPassword"
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
              label={newPasswordLabel}
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
              value => value === getValue(form, 'newPassword'),
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
        <LoadingButton type="submit" loading={form.submitting}>
          {t('changePassword.changePassword')}
        </LoadingButton>
      </Form>
    );
  },
);