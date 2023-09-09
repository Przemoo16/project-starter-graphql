import { createDOM } from '@builder.io/qwik/testing';
import { expect, test } from 'vitest';

import { Title } from './title';

test(`[Title Component]: displays only the app name if the page title is missing`, async () => {
  const { screen, render } = await createDOM();

  await render(<Title appName="Test App" pageTitle="" />);

  expect(screen.outerHTML).toContain('<title>Test App</title>');
});

test(`[Title Component]: displays both the app name and the page title`, async () => {
  const { screen, render } = await createDOM();

  await render(<Title appName="Test App" pageTitle="Test Page" />);

  expect(screen.outerHTML).toContain('<title>Test Page | Test App</title>');
});
