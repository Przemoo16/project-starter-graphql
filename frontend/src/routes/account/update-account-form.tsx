import { $, component$, type Signal } from '@builder.io/qwik';
import {
  FormError,
  type InitialValues,
  maxLength,
  required,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate, useSpeakContext, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MAX_FULL_NAME_LENGTH } from '~/routes/schema-config';
import { getClientRequestSender } from '~/services/requests/get-client.request-sender';
import { updateMe } from '~/services/user/update-me';

export type UpdateAccountFormSchema = {
  fullName: string;
};

interface UpdateAccountFormProps {
  loader: Readonly<Signal<InitialValues<UpdateAccountFormSchema>>>;
}

export const UpdateAccountForm = component$(
  ({ loader }: UpdateAccountFormProps) => {
    const t = useTranslate();
    const ctx = useSpeakContext();
    const [updateAccountForm, UpdateAccount] = useForm<UpdateAccountFormSchema>(
      {
        loader,
      },
    );

    const handleSubmit = $<SubmitHandler<UpdateAccountFormSchema>>(
      async (values, _event) => {
        const { problems } = await updateMe(
          getClientRequestSender(),
          values.fullName,
        );

        if (problems) {
          throw new FormError<UpdateAccountFormSchema>(
            inlineTranslate('updateAccount.updateAccountError', ctx),
          );
        }
        setResponse(updateAccountForm, {
          message: inlineTranslate('updateAccount.updateAccountSuccess', ctx),
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
          {t('updateAccount.updateAccount')}
        </button>
      </UpdateAccount.Form>
    );
  },
);
