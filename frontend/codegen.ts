import type { CodegenConfig } from '@graphql-codegen/cli';

const config: CodegenConfig = {
  overwrite: true,
  schema: 'http://proxy/api/graphql',
  generates: {
    'src/services/graphql.ts': {
      plugins: ['typescript'],
    },
  },
};

export default config;
