interface Problem {
  __typename?: string;
}

export const isProblemPresent = (problems: Problem[], type: string) =>
  problems.some(problem => problem.__typename === type);
