import { $, component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  routeLoader$,
  useNavigate,
} from '@builder.io/qwik-city';
import {
  custom$,
  email,
  FormError,
  getValue,
  type InitialValues,
  maxLength,
  minLength,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import {
  inlineTranslate,
  Speak,
  useSpeakContext,
  useTranslate,
} from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MAX_FULL_NAME_LENGTH, MIN_PASSWORD_LENGTH } from '~/constants';
import { isProblemPresent } from '~/libs/api/errors';
import { register } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.register.head.title',
};

type RegisterForm = {
  fullName: string;
  email: string;
  password: string;
  repeatPassword: string;
};

export const useFormLoader = routeLoader$<InitialValues<RegisterForm>>(() => ({
  fullName: '',
  email: '',
  password: '',
  repeatPassword: '',
}));

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Register />
  </Speak>
));

const Register = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const nav = useNavigate();
  const [loginForm, { Form, Field }] = useForm<RegisterForm>({
    loader: useFormLoader(),
  });

  const handleSubmit = $<SubmitHandler<RegisterForm>>(
    async (values, _event) => {
      const {
        createUser: { problems },
      } = await register(values.fullName, values.email, values.password);

      if (!problems) {
        await nav('/login');
      }

      let emailError = '';
      let generalError = '';
      if (isProblemPresent(problems, 'UserAlreadyExistsProblem')) {
        emailError = inlineTranslate('auth.userAlreadyExists', ctx);
      } else {
        generalError = inlineTranslate('auth.registerError', ctx);
      }
      throw new FormError<RegisterForm>(generalError, {
        email: emailError,
      });
    },
  );

  const fullNameLabel = t('auth.fullName');
  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');
  const repeatPasswordLabel = t('auth.repeatPassword');

  return (
    <Form onSubmit$={handleSubmit}>
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
      <Field
        name="email"
        validate={[
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
      <Field
        name="password"
        validate={[
          required(t('validation.required')),
          minLength(
            MIN_PASSWORD_LENGTH,
            t('validation.minPassword', { min: MIN_PASSWORD_LENGTH }),
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
        name="repeatPassword"
        validate={[
          required(t('validation.required')),
          custom$(
            value => value === getValue(loginForm, 'password'),
            t(`validation.passwordMatch`),
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
      <div>{loginForm.response.message}</div>
      <button type="submit" disabled={loginForm.submitting}>
        {t('auth.getStarted')}
      </button>
    </Form>
  );
});
