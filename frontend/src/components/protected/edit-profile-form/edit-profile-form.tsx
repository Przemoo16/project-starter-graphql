import {
  $,
  component$,
  type PropFunction,
  type Signal,
} from '@builder.io/qwik';
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

import { FormBody } from '~/components/common/form-body/form-body';
import { SubmitButton } from '~/components/common/submit-button/submit-button';
import { TextInput } from '~/components/common/text-input/text-input';
import { MAX_FULL_NAME_LENGTH } from '~/routes/schema-config';
import { type UpdateMeInput } from '~/services/graphql';

export type EditProfileFormSchema = {
  fullName: string;
};

interface EditProfileFormProps {
  loader: Readonly<Signal<InitialValues<EditProfileFormSchema>>>;
  onSubmit$: PropFunction<
    (input: UpdateMeInput) => Promise<EditProfileFormSchema>
  >;
}

export const EditProfileForm = component$<EditProfileFormProps>(
  ({ loader, onSubmit$ }) => {
    const t = inlineTranslate();
    const [form, { Form, Field }] = useForm<EditProfileFormSchema>({
      loader,
    });

    const handleSubmit = $<SubmitHandler<EditProfileFormSchema>>(
      async ({ fullName }, _event) => {
        const t = inlineTranslate();
        const user = await onSubmit$({ fullName });
        setResponse(form, {
          message: t('account.profileSaved'),
        });
        reset(form, { initialValues: user });
      },
    );

    const fullNameLabel = t('app.ui.fullName');

    return (
      <Form onSubmit$={handleSubmit} shouldDirty>
        <FormBody>
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
          <SubmitButton submitting={form.submitting}>
            {t('account.saveProfile')}
          </SubmitButton>
        </FormBody>
      </Form>
    );
  },
);
