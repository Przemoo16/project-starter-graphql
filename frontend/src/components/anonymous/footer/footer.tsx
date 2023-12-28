import { component$ } from '@builder.io/qwik';
import { inlineTranslate } from 'qwik-speak';

interface FooterProps {
  year: number;
}

export const Footer = component$(({ year }: FooterProps) => {
  const t = inlineTranslate();

  return (
    <footer class="footer footer-center p-5">
      <p>
        © {t('app.appName')} {year}
      </p>
    </footer>
  );
});
