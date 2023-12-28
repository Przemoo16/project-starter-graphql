import { $, component$, type QRL, type Signal } from '@builder.io/qwik';
import {
  type InitialValues,
  maxLength,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { LoadingButton } from '~/components/common/loading-button/loading-button';
import { TextInput } from '~/components/common/text-input/text-input';
import { MAX_FULL_NAME_LENGTH } from '~/routes/schema-config';
import { type UpdateMeInput } from '~/services/graphql';

export type UpdateAccountFormSchema = {
  fullName: string;
};

interface UpdateAccountFormProps {
  loader: Readonly<Signal<InitialValues<UpdateAccountFormSchema>>>;
  onSubmit: QRL<(input: UpdateMeInput) => Promise<UpdateAccountFormSchema>>;
}

export const UpdateAccountForm = component$(
  ({ loader, onSubmit }: UpdateAccountFormProps) => {
    const t = inlineTranslate();
    const [form, { Form, Field }] = useForm<UpdateAccountFormSchema>({
      loader,
    });

    const handleSubmit = $<SubmitHandler<UpdateAccountFormSchema>>(
      async ({ fullName }, _event) => {
        const t = inlineTranslate();
        const user = await onSubmit({ fullName });
        setResponse(form, {
          message: t('updateAccount.updateAccountSuccess'),
        });
        reset(form, { initialValues: user });
      },
    );

    const fullNameLabel = t('account.fullName');

    return (
      <Form onSubmit$={handleSubmit} shouldDirty>
        <Field
          name="fullName"
          validate={[
            // @ts-expect-error: FIXME: https://github.com/fabian-hiller/modular-forms/issues/158
            required(t('validation.fieldRequired')),
            maxLength(
              MAX_FULL_NAME_LENGTH,
              t('validation.fullNameTooLong', { max: MAX_FULL_NAME_LENGTH }),
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
        <div>{form.response.message}</div>
        <LoadingButton type="submit" loading={form.submitting}>
          {t('updateAccount.updateAccount')}
        </LoadingButton>
      </Form>
    );
  },
);
