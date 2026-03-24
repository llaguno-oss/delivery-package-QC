import { useRef, useState } from 'react';
import { Download, Upload, RotateCcw, Package } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { downloadConfig, readConfigFile } from '../../utils/jsonIO';
import { validateConfig } from '../../utils/validation';
import { ConfirmDialog } from '../shared/ConfirmDialog';

export function AppHeader() {
  const exportConfig = useConfigStore((s) => s.exportConfig);
  const importConfig = useConfigStore((s) => s.importConfig);
  const resetConfig = useConfigStore((s) => s.resetConfig);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);

  const handleExport = () => {
    downloadConfig(exportConfig());
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const raw = await readConfigFile(file);
      if (!validateConfig(raw)) {
        setImportError('The selected file is not a valid QC config.');
        return;
      }
      importConfig(raw);
      setImportError(null);
    } catch {
      setImportError('Failed to read file. Make sure it is a valid JSON file.');
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <>
      <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)] bg-[var(--color-surface-1)]">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-[var(--color-accent-dim)] text-[var(--color-accent)]">
            <Package size={20} />
          </div>
          <div>
            <h1 className="text-base font-bold text-[var(--color-text-primary)] leading-tight">
              Delivery Package QC
            </h1>
            <p className="text-xs text-[var(--color-text-muted)]">
              Package scan configuration
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {importError && (
            <span className="text-xs text-[var(--color-danger)] mr-2">{importError}</span>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={handleImport}
            className="hidden"
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="qc-btn-secondary"
            title="Import config"
          >
            <Upload size={14} />
            Import
          </button>

          <button onClick={handleExport} className="qc-btn-secondary" title="Export config">
            <Download size={14} />
            Export
          </button>

          <div className="w-px h-6 bg-[var(--color-border)] mx-1" />

          <button
            onClick={() => setResetDialogOpen(true)}
            className="qc-btn-ghost"
            title="Reset config"
          >
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </header>

      <ConfirmDialog
        open={resetDialogOpen}
        onClose={() => setResetDialogOpen(false)}
        onConfirm={resetConfig}
        title="Reset configuration"
        message="This will clear all configured parameters and return to the default empty state. This cannot be undone."
        confirmLabel="Reset"
        variant="danger"
      />
    </>
  );
}
