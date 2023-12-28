import { component$ } from '@builder.io/qwik';

interface TitleProps {
  appName: string;
  pageTitle: string;
}

export const TitleHead = component$(({ appName, pageTitle }: TitleProps) => {
  const title = pageTitle ? `${pageTitle} | ${appName}` : appName;

  return <title>{title}</title>;
});
