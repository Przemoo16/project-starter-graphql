import { $, component$, type QRL, type Signal } from '@builder.io/qwik';
import {
  type InitialValues,
  maxLength,
  required,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate, useSpeakContext, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

import { MAX_FULL_NAME_LENGTH } from './schema-config';

export type UpdateAccountFormSchema = {
  fullName: string;
};

interface UpdateAccountFormProps {
  onSubmit: QRL<SubmitHandler<UpdateAccountFormSchema>>;
  loader: Readonly<Signal<InitialValues<UpdateAccountFormSchema>>>;
}

export const UpdateAccountForm = component$(
  ({ onSubmit, loader }: UpdateAccountFormProps) => {
    const t = useTranslate();
    const ctx = useSpeakContext();
    const [updateAccountForm, UpdateAccount] = useForm<UpdateAccountFormSchema>(
      {
        loader,
      },
    );

    const handleSubmit = $<SubmitHandler<UpdateAccountFormSchema>>(
      async (values, event) => {
        await onSubmit(values, event);

        setResponse(updateAccountForm, {
          message: inlineTranslate('account.updateAccountSuccess', ctx),
        });
      },
    );

    const fullNameLabel = t('account.fullName');

    return (
      <UpdateAccount.Form onSubmit$={handleSubmit} shouldDirty>
        <UpdateAccount.Field
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
        </UpdateAccount.Field>
        <div>{updateAccountForm.response.message}</div>
        <button type="submit" disabled={updateAccountForm.submitting}>
          {t('account.updateAccount')}
        </button>
      </UpdateAccount.Form>
    );
  },
);
