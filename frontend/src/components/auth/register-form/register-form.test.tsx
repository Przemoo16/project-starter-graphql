import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { type UserCreateInput } from '~/services/graphql';
import { fillInput } from '~/tests/input';

import { RegisterForm } from './register-form';

const ON_SUBMIT = $(async (_input: UserCreateInput) => {});

describe('[RegisterForm Component]', () => {
  test(`doesn't display error if full name passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'Test User');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if full name is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if full name is too long`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'T'.repeat(129));
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error') as HTMLDivElement;
    expect(error.textContent).toContain('fullNameTooLong');
  });

  test(`doesn't display error if email passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test@email.com');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if email is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if email is invalid`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error') as HTMLDivElement;
    expect(error.textContent).toContain('invalidEmail');
  });

  test(`doesn't display error if password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#password') as HTMLInputElement;

    await fillInput(input, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if password is too short`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#password') as HTMLInputElement;

    await fillInput(input, userEvent, 'p');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error') as HTMLDivElement;
    expect(error.textContent).toContain('passwordTooShort');
  });

  test(`doesn't display error if repeated password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const passwordInput = screen.querySelector('#password') as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(passwordInput, userEvent, 'testPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#repeatedPassword-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if repeated password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector(
      '#repeatedPassword-error',
    ) as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if repeated password doesn't match`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const passwordInput = screen.querySelector('#password') as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(passwordInput, userEvent, 'testPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'invalidPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector(
      '#repeatedPassword-error',
    ) as HTMLDivElement;
    expect(error.textContent).toContain('passwordDoesNotMatch');
  });

  test(`resets form after submit`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const fullNameInput = screen.querySelector('#fullName') as HTMLInputElement;
    const emailInput = screen.querySelector('#email') as HTMLInputElement;
    const passwordInput = screen.querySelector('#password') as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(fullNameInput, userEvent, 'Test User');
    await fillInput(emailInput, userEvent, 'test@email.com');
    await fillInput(passwordInput, userEvent, 'testPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    expect(fullNameInput.value).toEqual('');
    expect(emailInput.value).toEqual('');
    expect(passwordInput.value).toEqual('');
    expect(repeatedPasswordInput.value).toEqual('');
  });

  // FIXME: Enable the test after this is resolved: https://github.com/fabian-hiller/modular-forms/issues/161
  test.skip(`displays success message`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RegisterForm onSubmit$={ON_SUBMIT} />);
    const fullNameInput = screen.querySelector('#fullName') as HTMLInputElement;
    const emailInput = screen.querySelector('#email') as HTMLInputElement;
    const passwordInput = screen.querySelector('#password') as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(fullNameInput, userEvent, 'Test User');
    await fillInput(emailInput, userEvent, 'test@email.com');
    await fillInput(passwordInput, userEvent, 'testPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    expect(screen.textContent).toContain('registerSuccess');
  });
});
