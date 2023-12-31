import { type ButtonHTMLAttributes, component$, Slot } from '@builder.io/qwik';

interface LoadingButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading: boolean;
  additionalClass?: string;
}

export const LoadingButton = component$<LoadingButtonProps>(
  ({ loading, additionalClass, ...rest }) => (
    <button disabled={loading} class={`btn ${additionalClass}`} {...rest}>
      {loading && <span class="loading loading-dots" />}
      {!loading && <Slot />}
    </button>
  ),
);
