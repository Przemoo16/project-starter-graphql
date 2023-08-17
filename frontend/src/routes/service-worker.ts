/*
 * WHAT IS THIS FILE?
 *
 * The service-worker.ts file is used to have state of the art prefetching.
 * https://qwik.builder.io/qwikcity/prefetching/overview/
 *
 * Qwik uses a service worker to speed up your site and reduce latency, ie, not used in the traditional way of offline.
 * You can also use this file to add more functionality that runs in the service worker.
 */
import { setupServiceWorker } from '@builder.io/qwik-city/service-worker';

setupServiceWorker();

addEventListener('install', () => {
  const handler = async (): Promise<void> => {
    await self.skipWaiting();
  };
  void handler();
});

addEventListener('activate', () => {
  const handler = async (): Promise<void> => {
    await self.clients.claim();
  };
  void handler();
});

declare const self: ServiceWorkerGlobalScope;
