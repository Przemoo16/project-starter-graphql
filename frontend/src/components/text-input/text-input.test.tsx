import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { expect, test } from 'vitest';

import { TextInput } from './text-input';

const EMPTY_CALLBACK = $(() => {});

test(`[TextInput Component]: doesn't render label`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      value=""
      error=""
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  const label = screen.querySelector('label[for="test"]') as HTMLLabelElement;
  expect(label).toBeUndefined();
});

test(`[TextInput Component]: renders label`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error=""
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  const label = screen.querySelector('label[for="test"]') as HTMLLabelElement;
  expect(label.innerHTML).toContain('Test Label ');
});

test(`[TextInput Component]: renders required label`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error=""
      required
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  const label = screen.querySelector('label[for="test"]') as HTMLLabelElement;
  expect(label.innerHTML).toContain('Test Label <span>*</span>');
});

test(`[TextInput Component]: renders input without error`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error=""
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  const input = screen.querySelector('#test') as HTMLInputElement;
  expect(input.outerHTML).toContain(
    'aria-errormessage="test-error" aria-invalid="false"',
  );
  const error = screen.querySelector('#test-error') as HTMLDivElement;
  expect(error).toBeUndefined();
});

test(`[TextInput Component]: renders input with error`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error="Test Error"
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  const input = screen.querySelector('#test') as HTMLInputElement;
  expect(input.outerHTML).toContain(
    'aria-errormessage="test-error" aria-invalid="true"',
  );
  const error = screen.querySelector('#test-error') as HTMLDivElement;
  expect(error.innerHTML).toEqual('Test Error');
});
