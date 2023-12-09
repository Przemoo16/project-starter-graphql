import { expect, test } from 'vitest';

import { isProblemPresent } from './is-problem-present';

test(`[isProblemPresent function]: returns true if specified problem is present`, () => {
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

test(`[isProblemPresent function]: returns false if specified problem is not present`, () => {
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
