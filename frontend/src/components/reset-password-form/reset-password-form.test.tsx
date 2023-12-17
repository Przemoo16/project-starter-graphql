import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { fillInput } from '~/tests/input';

import { ResetPasswordForm } from './reset-password-form';

const ON_SUBMIT = $(async (_password: string) => {});

describe('[ResetPasswordForm Component]', () => {
  test(`doesn't display error if password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#password') as HTMLInputElement;

    await fillInput(input, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error') as HTMLDivElement;
    expect(error.innerHTML).toContain('fieldRequired');
  });

  test(`displays error if password is too short`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#password') as HTMLInputElement;

    await fillInput(input, userEvent, 'p');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error') as HTMLDivElement;
    expect(error.innerHTML).toContain('passwordTooShort');
  });

  test(`doesn't display error if repeated password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);
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
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector(
      '#repeatedPassword-error',
    ) as HTMLDivElement;
    expect(error.innerHTML).toContain('fieldRequired');
  });

  test(`displays error if repeated password doesn't match`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);
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
    expect(error.innerHTML).toContain('passwordDoesNotMatch');
  });

  test(`resets form after submit`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);
    const passwordInput = screen.querySelector('#password') as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(passwordInput, userEvent, 'testPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    expect(passwordInput.value).toEqual('');
    expect(repeatedPasswordInput.value).toEqual('');
  });

  // FIXME: Enable the test after this is resolved: https://github.com/fabian-hiller/modular-forms/issues/161
  test.skip(`displays success message`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ResetPasswordForm onSubmit={ON_SUBMIT} />);
    const passwordInput = screen.querySelector('#password') as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(passwordInput, userEvent, 'testPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    expect(screen.innerHTML).toContain('resetPasswordSuccess');
  });
});
