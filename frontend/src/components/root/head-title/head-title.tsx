import { component$ } from '@builder.io/qwik';

interface HeadTitleProps {
  appName: string;
  pageTitle: string;
}

export const HeadTitle = component$(
  ({ appName, pageTitle }: HeadTitleProps) => {
    const title = pageTitle ? `${pageTitle} | ${appName}` : appName;

    return <title>{title}</title>;
  },
);
