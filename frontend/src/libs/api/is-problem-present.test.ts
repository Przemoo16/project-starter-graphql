import { describe, expect, test } from 'vitest';

import { isProblemPresent } from './is-problem-present';

describe('[isProblemPresent function]', () => {
  test(`returns true if specified problem is present`, () => {
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

  test(`returns false if specified problem is not present`, () => {
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
});
