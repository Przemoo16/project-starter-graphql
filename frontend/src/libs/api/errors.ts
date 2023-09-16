interface Problem {
  __typename: string;
}

export const isProblemPresent = (problems: Problem[], type: string): boolean =>
  problems.some(problem => problem.__typename === type);

interface ErrorLocation {
  line: number;
  column: number;
}

export interface GraphQLError {
  message: string;
  locations: ErrorLocation[];
  path: string[];
}

export class RequestError extends Error {
  errors: GraphQLError[];

  constructor(
    errors: GraphQLError[],
    message?: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.errors = errors;
    Error.captureStackTrace(this, RequestError);
  }
}
