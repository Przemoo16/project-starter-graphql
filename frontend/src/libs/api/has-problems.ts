export const hasProblems = (
  data: Record<string, any>,
): data is { problems: any } => 'problems' in data;
