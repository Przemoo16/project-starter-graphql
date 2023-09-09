import { expect, test } from 'vitest';

import { isProblemPresent } from './errors';

test(`[isProblemPresent function]: finds specified problem`, () => {
  const problems = [
    {
      __typename: 'test1',
    },
    {
      __typename: 'test2',
    },
  ];

  const isPresent = isProblemPresent(problems, 'test1');

  expect(isPresent).toBe(true);
});

test(`[isProblemPresent function]: doesn't find specified problem`, () => {
  const problems = [
    {
      __typename: 'test1',
    },
    {
      __typename: 'test2',
    },
  ];

  const isPresent = isProblemPresent(problems, 'test3');

  expect(isPresent).toBe(false);
});
