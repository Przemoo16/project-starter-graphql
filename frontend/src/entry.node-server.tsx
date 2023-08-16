/*
 * WHAT IS THIS FILE?
 *
 * It's the entry point for the Express HTTP server when building for production.
 *
 * Learn more about Node.js server integrations here:
 * - https://qwik.builder.io/docs/deployments/node/
 *
 */
import { createServer } from 'node:http';

import { createQwikCity } from '@builder.io/qwik-city/middleware/node';
import qwikCityPlan from '@qwik-city-plan';
import { manifest } from '@qwik-client-manifest';

import render from './entry.ssr';

// Allow for dynamic port
const PORT = process.env.PORT ?? 5173;

// Create the Qwik City express middleware
const { router, notFound, staticFile } = createQwikCity({
  render,
  qwikCityPlan,
  manifest,
});

const server = createServer();

server.on('request', (req, res) => {
  void staticFile(req, res, () => {
    void router(req, res, () => {
      void notFound(req, res, () => {});
    });
  });
});

server.listen(PORT);
