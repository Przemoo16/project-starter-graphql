import { type ButtonHTMLAttributes, component$, Slot } from '@builder.io/qwik';

interface LoadingButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading: boolean;
}

export const LoadingButton = component$(
  ({ loading, ...rest }: LoadingButtonProps) => (
    <button disabled={loading} class="btn btn-primary" {...rest}>
      {loading && <span class="loading loading-dots" />}
      {!loading && <Slot />}
    </button>
  ),
);
