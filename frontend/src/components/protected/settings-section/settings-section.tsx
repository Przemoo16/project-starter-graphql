import { component$, Slot } from '@builder.io/qwik';

interface SettingsSectionProps {
  title: string;
}

export const SettingsSection = component$<SettingsSectionProps>(({ title }) => (
  <section class="card w-11/12 max-w-md bg-base-100 shadow-xl">
    <div class="card-body gap-5">
      <h2 class="text-center text-2xl font-bold">{title}</h2>
      <Slot />
    </div>
  </section>
));
