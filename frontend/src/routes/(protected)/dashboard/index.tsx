import { component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.dashboard.title'),
    meta: [
      {
        name: 'description',
        content: t('app.head.dashboard.description'),
      },
    ],
  };
};

export default component$(() => {
  useSpeak({ assets: ['dashboard'] });

  return <Dashboard />;
});

const Dashboard = component$(() => {
  const t = inlineTranslate();

  return (
    <div class="grid h-full place-items-center">
      <h1 class="text-center text-5xl font-bold">{t('dashboard.dashboard')}</h1>
    </div>
  );
});
