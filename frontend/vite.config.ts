import { qwikVite } from '@builder.io/qwik/optimizer';
import { qwikCity } from '@builder.io/qwik-city/vite';
import { qwikSpeakInline } from 'qwik-speak/inline';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig(() => {
  return {
    plugins: [
      qwikCity(),
      qwikVite(),
      qwikSpeakInline({
        supportedLangs: ['en-US'],
        defaultLang: 'en-US',
        assetsPath: 'i18n',
      }),
      tsconfigPaths(),
    ],
    server: {
      host: true,
      port: 80,
      strictPort: true,
    },
    dev: {
      headers: {
        'Cache-Control': 'public, max-age=0',
      },
    },
    preview: {
      headers: {
        'Cache-Control': 'public, max-age=600',
      },
    },
  };
});
