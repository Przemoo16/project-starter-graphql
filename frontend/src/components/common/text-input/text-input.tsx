import { component$, type PropFunction } from '@builder.io/qwik';
import { type FieldElement, type FieldEvent } from '@modular-forms/qwik';

type TextInputProps = {
  name: string;
  type: 'text' | 'email' | 'tel' | 'password' | 'url' | 'date';
  label?: string;
  placeholder?: string;
  value: string | undefined;
  error: string;
  required?: boolean;
  ref: (element: Element) => void;
  onInput$: PropFunction<(event: FieldEvent, element: FieldElement) => void>;
  onChange$: PropFunction<(event: FieldEvent, element: FieldElement) => void>;
  onBlur$: PropFunction<(event: FieldEvent, element: FieldElement) => void>;
};

export const TextInput = component$<TextInputProps>(
  ({ label, error, name, required, ...props }) => {
    const inputErrorClass = error ? 'input-error' : '';
    return (
      <div class="form-control">
        {label && (
          <label for={name} class="label">
            <span class="label-text">
              {label} {required && <span class="text-error">*</span>}
            </span>
          </label>
        )}
        <input
          {...props}
          id={name}
          aria-errormessage={`${name}-error`}
          aria-invalid={!!error}
          class={`input input-bordered ${inputErrorClass}`}
        />
        {error && (
          <div id={`${name}-error`} class="mt-2 text-error">
            {error}
          </div>
        )}
      </div>
    );
  },
);
