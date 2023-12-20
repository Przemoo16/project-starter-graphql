export const hasProblems = (
  data: Record<string, unknown>,
): data is { problems: unknown } => 'problems' in data;
