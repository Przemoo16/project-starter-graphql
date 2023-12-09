import { $, component$, type QRL, type Signal } from '@builder.io/qwik';
import {
  type InitialValues,
  maxLength,
  required,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MAX_FULL_NAME_LENGTH } from '~/routes/schema-config';

export type UpdateAccountFormSchema = {
  fullName: string;
};

interface UpdateAccountFormProps {
  loader: Readonly<Signal<InitialValues<UpdateAccountFormSchema>>>;
  onSubmit: QRL<(fullName: string) => Promise<string>>;
}

export const UpdateAccountForm = component$(
  ({ loader, onSubmit }: UpdateAccountFormProps) => {
    const t = inlineTranslate();
    const [updateAccountForm, { Form, Field }] =
      useForm<UpdateAccountFormSchema>({
        loader,
      });

    const handleSubmit = $<SubmitHandler<UpdateAccountFormSchema>>(
      async ({ fullName }, _event) => {
        const message = await onSubmit(fullName);
        setResponse(updateAccountForm, {
          message,
        });
      },
    );

    const fullNameLabel = t('account.fullName');

    return (
      <Form onSubmit$={handleSubmit} shouldDirty>
        <Field
          name="fullName"
          validate={[
            required(t('validation.required')),
            maxLength(
              MAX_FULL_NAME_LENGTH,
              t('validation.maxFullName', { max: MAX_FULL_NAME_LENGTH }),
            ),
          ]}
        >
          {(field, props) => (
            <TextInput
              {...props}
              type="text"
              label={fullNameLabel}
              placeholder="Jon Doe"
              value={field.value}
              error={field.error}
              required
            />
          )}
        </Field>
        <div>{updateAccountForm.response.message}</div>
        <button type="submit" disabled={updateAccountForm.submitting}>
          {t('updateAccount.updateAccount')}
        </button>
      </Form>
    );
  },
);
