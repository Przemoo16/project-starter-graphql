export const fillInput = async (
  input: HTMLInputElement,
  userEvent: (
    queryOrElement: string | Element | keyof HTMLElementTagNameMap | null,
    eventNameCamel: string | keyof WindowEventMap,
    eventPayload?: any,
  ) => Promise<void>,
  value: string,
) => {
  input.value = value;
  await userEvent(input, 'input', { target: { value } });
};
