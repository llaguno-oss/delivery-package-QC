import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { AlertTriangle } from 'lucide-react';

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  variant?: 'danger' | 'warning';
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirm',
  variant = 'danger',
}: ConfirmDialogProps) {
  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-150"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-150"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-100"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Dialog.Panel className="w-full max-w-md rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-1)] p-6 shadow-2xl">
              <div className="flex items-start gap-4">
                <div
                  className={`flex-shrink-0 p-2 rounded-lg ${
                    variant === 'danger'
                      ? 'bg-[var(--color-danger-dim)] text-[var(--color-danger)]'
                      : 'bg-[var(--color-warning-dim)] text-[var(--color-warning)]'
                  }`}
                >
                  <AlertTriangle size={20} />
                </div>
                <div>
                  <Dialog.Title className="text-base font-semibold text-[var(--color-text-primary)] mb-1">
                    {title}
                  </Dialog.Title>
                  <p className="text-sm text-[var(--color-text-muted)]">{message}</p>
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button onClick={onClose} className="qc-btn-secondary">
                  Cancel
                </button>
                <button
                  onClick={() => { onConfirm(); onClose(); }}
                  className={variant === 'danger' ? 'qc-btn-danger' : 'qc-btn-primary'}
                >
                  {confirmLabel}
                </button>
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}
