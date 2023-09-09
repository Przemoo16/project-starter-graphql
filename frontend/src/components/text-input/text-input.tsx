import {
  component$,
  type PropFunction,
  type QwikChangeEvent,
  type QwikFocusEvent,
} from '@builder.io/qwik';

type TextInputProps = {
  name: string;
  type: 'text' | 'email' | 'tel' | 'password' | 'url' | 'date';
  label?: string;
  placeholder?: string;
  value: string | undefined;
  error: string;
  required?: boolean;
  ref: PropFunction<(element: Element) => void>;
  onInput$: PropFunction<(event: Event, element: HTMLInputElement) => void>;
  onChange$: PropFunction<
    (
      event: QwikChangeEvent<HTMLInputElement>,
      element: HTMLInputElement,
    ) => void
  >;
  onBlur$: PropFunction<
    (event: QwikFocusEvent<HTMLInputElement>, element: HTMLInputElement) => void
  >;
};

export const TextInput = component$<TextInputProps>(
  ({ label, error, name, required, ...props }) => (
    <div>
      {label && (
        <label for={name}>
          {label} {required && <span>*</span>}
        </label>
      )}
      <input
        {...props}
        id={name}
        aria-invalid={!!error}
        aria-errormessage={`${name}-error`}
      />
      {error && <div id={`${name}-error`}>{error}</div>}
    </div>
  ),
);
