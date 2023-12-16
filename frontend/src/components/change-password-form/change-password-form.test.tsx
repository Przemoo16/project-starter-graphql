import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { fillInput } from '~/tests/input';

import { ChangePasswordForm } from './change-password-form';

const ON_SUBMIT = $(
  (_currentPassword: string, _newPassword: string) => 'Success',
);

describe('[ChangePasswordForm Component]', () => {
  test(`doesn't display error if current password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#currentPassword') as HTMLInputElement;

    await fillInput(input, userEvent, 'currentPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#currentPassword-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if current password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector(
      '#currentPassword-error',
    ) as HTMLDivElement;
    expect(error.innerHTML).toContain('required');
  });

  test(`doesn't display error if new password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#newPassword') as HTMLInputElement;

    await fillInput(input, userEvent, 'newPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#newPassword-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if new password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#newPassword-error') as HTMLDivElement;
    expect(error.innerHTML).toContain('required');
  });

  test(`displays error if new password is too short`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#newPassword') as HTMLInputElement;

    await fillInput(input, userEvent, 'p');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#newPassword-error') as HTMLDivElement;
    expect(error.innerHTML).toContain('minPassword');
  });

  test(`doesn't display error if repeated password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);
    const newPasswordInput = screen.querySelector(
      '#newPassword',
    ) as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(newPasswordInput, userEvent, 'newPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'newPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#repeatedPassword-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if repeated password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector(
      '#repeatedPassword-error',
    ) as HTMLDivElement;
    expect(error.innerHTML).toContain('required');
  });

  test(`displays error if repeated password doesn't match`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);
    const newPasswordInput = screen.querySelector(
      '#newPassword',
    ) as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(newPasswordInput, userEvent, 'newPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'invalidPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector(
      '#repeatedPassword-error',
    ) as HTMLDivElement;
    expect(error.innerHTML).toContain('passwordDoesNotMatch');
  });

  test(`resets form after submit`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<ChangePasswordForm onSubmit={ON_SUBMIT} />);
    const currentPasswordInput = screen.querySelector(
      '#currentPassword',
    ) as HTMLInputElement;
    const newPasswordInput = screen.querySelector(
      '#newPassword',
    ) as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(currentPasswordInput, userEvent, 'currentPassword');
    await fillInput(newPasswordInput, userEvent, 'newPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'newPassword');
    await userEvent('button[type="submit"]', 'submit');

    expect(currentPasswordInput.value).toEqual('');
    expect(newPasswordInput.value).toEqual('');
    expect(repeatedPasswordInput.value).toEqual('');
  });

  // FIXME: Enable the test after this is resolved: https://github.com/fabian-hiller/modular-forms/issues/161
  test.skip(`displays success message`, async () => {
    const { screen, render, userEvent } = await createDOM();
    const onSubmit = $(
      (_currentPassword: string, _newPassword: string) =>
        'Form has been submitted successfully',
    );
    await render(<ChangePasswordForm onSubmit={onSubmit} />);
    const currentPasswordInput = screen.querySelector(
      '#currentPassword',
    ) as HTMLInputElement;
    const newPasswordInput = screen.querySelector(
      '#newPassword',
    ) as HTMLInputElement;
    const repeatedPasswordInput = screen.querySelector(
      '#repeatedPassword',
    ) as HTMLInputElement;

    await fillInput(currentPasswordInput, userEvent, 'currentPassword');
    await fillInput(newPasswordInput, userEvent, 'newPassword');
    await fillInput(repeatedPasswordInput, userEvent, 'newPassword');
    await userEvent('button[type="submit"]', 'submit');

    expect(screen.innerHTML).toContain('Form has been submitted successfully');
  });
});
