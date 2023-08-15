import { component$ } from '@builder.io/qwik';

import ImgThunder from '~/media/thunder.png?jsx';

import styles from './hero.module.css';

export default component$(() => {
  return (
    <div class={['container', styles.hero]}>
      <ImgThunder class={styles['hero-image']} />
      <h1>
        So <span class="highlight">fantastic</span>
        <br />
        to have <span class="highlight">you</span> here
      </h1>
      <p>Have fun building your App with Qwik.</p>
      <div class={styles['button-group']}>
        <button
          onClick$={async () => {
            const defaults = {
              spread: 360,
              ticks: 70,
              gravity: 0,
              decay: 0.95,
              startVelocity: 30,
              colors: ['006ce9', 'ac7ff4', '18b6f6', '713fc2', 'ffffff'],
              origin: {
                x: 0.5,
                y: 0.35,
              },
            };

            async function loadConfetti(): Promise<(opts: any) => void> {
              return await new Promise<(opts: any) => void>(
                (resolve, reject) => {
                  // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
                  if ((globalThis as any).confetti) {
                    resolve((globalThis as any).confetti);
                    return;
                  }
                  const script = document.createElement('script');
                  script.src =
                    'https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js';
                  script.onload = () => {
                    resolve((globalThis as any).confetti);
                  };
                  script.onerror = reject;
                  document.head.appendChild(script);
                  script.remove();
                },
              );
            }

            const confetti = await loadConfetti();

            function shoot(): void {
              confetti({
                ...defaults,
                particleCount: 80,
                scalar: 1.2,
              });

              confetti({
                ...defaults,
                particleCount: 60,
                scalar: 0.75,
              });
            }

            setTimeout(shoot, 0);
            setTimeout(shoot, 100);
            setTimeout(shoot, 200);
            setTimeout(shoot, 300);
            setTimeout(shoot, 400);
          }}
        >
          Time to celebrate
        </button>
        <a
          href="https://qwik.builder.io/docs"
          target="_blank"
          class="button button-dark"
        >
          Explore the docs
        </a>
      </div>
    </div>
  );
});
