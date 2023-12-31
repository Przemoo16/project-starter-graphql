import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { LoadingButton } from './loading-button';

describe('[LoadingButton Component]', () => {
  test(`doesn't disable button in non-loading state`, async () => {
    const { screen, render } = await createDOM();

    await render(<LoadingButton loading={false}>Test Button</LoadingButton>);

    const button = screen.querySelector('button') as HTMLButtonElement;
    expect(button.disabled).toBe(false);
  });

  test(`disables button in loading state`, async () => {
    const { screen, render } = await createDOM();

    await render(<LoadingButton loading={true}>Test Button</LoadingButton>);

    const button = screen.querySelector('button') as HTMLButtonElement;
    expect(button.disabled).toBe(true);
  });

  test(`displays text in non-loading state`, async () => {
    const { screen, render } = await createDOM();

    await render(<LoadingButton loading={false}>Test Button</LoadingButton>);

    const button = screen.querySelector('button') as HTMLButtonElement;
    expect(button.textContent).toEqual('Test Button');
  });

  test(`doesn't display text in loading state`, async () => {
    const { screen, render } = await createDOM();

    await render(<LoadingButton loading={true}>Test Button</LoadingButton>);

    const button = screen.querySelector('button') as HTMLButtonElement;
    expect(button.textContent).toEqual('');
  });

  test(`doesn't display loading icon in non-loading state`, async () => {
    const { screen, render } = await createDOM();

    await render(<LoadingButton loading={false}>Test Button</LoadingButton>);

    const span = screen.querySelector('span');
    expect(span).toBeUndefined();
  });

  test(`displays loading icon in loading state`, async () => {
    const { screen, render } = await createDOM();

    await render(<LoadingButton loading={true}>Test Button</LoadingButton>);

    const span = screen.querySelector('span');
    expect(span).toBeDefined();
  });

  test(`adds additional class to the button`, async () => {
    const { screen, render } = await createDOM();

    await render(
      <LoadingButton loading={false} additionalClass="test">
        Test Button
      </LoadingButton>,
    );

    const button = screen.querySelector('button') as HTMLButtonElement;
    expect(button.classList).toContain('test');
  });
});
