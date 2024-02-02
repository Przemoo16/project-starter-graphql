import { nodeServerAdapter } from '@builder.io/qwik-city/adapters/node-server/vite';
import { extendConfig } from '@builder.io/qwik-city/vite';

import baseConfig from '../../vite.config';

// @ts-expect-error: FIXME: Fix after vite and qwik versions are compatible
export default extendConfig(baseConfig, () => {
  return {
    build: {
      ssr: true,
      rollupOptions: {
        input: ['src/entry.node-server.tsx', '@qwik-city-plan'],
      },
    },
    plugins: [nodeServerAdapter({ name: 'node-server' })],
  };
});
