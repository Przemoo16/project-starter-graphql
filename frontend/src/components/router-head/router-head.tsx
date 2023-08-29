import { component$ } from '@builder.io/qwik';
import { useDocumentHead, useLocation } from '@builder.io/qwik-city';
import { useTranslate } from 'qwik-speak';

/**
 * The RouterHead component is placed inside of the document `<head>` element.
 */
export const RouterHead = component$(() => {
  const t = useTranslate();
  const head = useDocumentHead();
  const loc = useLocation();

  const title = head.title
    ? `${t(head.title)} | ${t('runtime.app.head.title')}`
    : t('runtime.app.head.title');

  return (
    <>
      <title>{title}</title>

      <link rel="canonical" href={loc.url.href} />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <link rel="icon" type="image/svg+xml" href="/favicon.svg" />

      {head.meta.map(m => (
        <meta key={m.key} {...m} />
      ))}

      {head.links.map(l => (
        <link key={l.key} {...l} />
      ))}

      {head.styles.map(s => (
        <style key={s.key} {...s.props} dangerouslySetInnerHTML={s.style} />
      ))}
    </>
  );
});
