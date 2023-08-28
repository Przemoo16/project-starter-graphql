import { server$ } from '@builder.io/qwik-city';
import type { LoadTranslationFn, Translation, TranslationFn } from 'qwik-speak';

const translationData = import.meta.glob<Translation>('/i18n/**/*.json');

const loadTranslation$: LoadTranslationFn = server$(
  async (lang: string, asset: string) =>
    await translationData[`/i18n/${lang}/${asset}.json`]?.(),
);

export const translationFn: TranslationFn = {
  loadTranslation$,
};
