import { $, component$, type PropFunction, useSignal } from '@builder.io/qwik';
import { inlineTranslate } from 'qwik-speak';

import { LoadingButton } from '~/components/common/loading-button/loading-button';

interface DeleteAccountModalProps {
  onDelete$: PropFunction<() => Promise<void>>;
}

export const DeleteAccountModal = component$<DeleteAccountModalProps>(
  ({ onDelete$ }) => {
    const t = inlineTranslate();
    const requestPending = useSignal(false);

    const onDeleteAccount = $(async () => {
      requestPending.value = true;
      await onDelete$();
      requestPending.value = false;
    });

    return (
      <>
        <button
          class="btn btn-error"
          onClick$={() => {
            const element = document.getElementById(
              'modal',
            ) as HTMLDialogElement;
            element.showModal();
          }}
        >
          {t('account.deleteAccount')}
        </button>
        <dialog id="modal" class="modal">
          <div class="modal-box">
            <h3 class="text-center text-lg font-bold">
              {t('account.deleteYourAccount')}
            </h3>
            <p class="mt-6">{t('account.deleteAccountWarning')}</p>
            <div class="modal-action">
              <form method="dialog">
                <button class="btn w-28">{t('account.noKeepIt')}</button>
              </form>
              <LoadingButton
                onClick$={onDeleteAccount}
                loading={requestPending.value}
                additionalClass="btn-error w-28"
              >
                {t('account.yesDelete')}
              </LoadingButton>
            </div>
          </div>
        </dialog>
      </>
    );
  },
);
