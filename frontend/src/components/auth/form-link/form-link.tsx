import { component$, Slot } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';

interface FormLinkProps {
  href: string;
}

export const FormLink = component$(({ href }: FormLinkProps) => (
  <Link href={href} class="link-hover link link-primary">
    <Slot />
  </Link>
));
