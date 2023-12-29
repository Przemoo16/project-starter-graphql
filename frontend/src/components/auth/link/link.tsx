import { component$, Slot } from '@builder.io/qwik';
import { Link as BaseLink } from '@builder.io/qwik-city';

interface LinkProps {
  href: string;
}

export const Link = component$<LinkProps>(({ href }) => (
  <BaseLink href={href} class="link-hover link link-primary">
    <Slot />
  </BaseLink>
));
