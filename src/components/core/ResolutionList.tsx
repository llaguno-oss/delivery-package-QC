import { useState } from 'react';
import { Plus, X, Monitor } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';

const PRESETS = ['1920x1080', '1280x720', '3840x2160', '4096x2160', '720x576', '720x486'];

export function ResolutionList() {
  const resolutions = useConfigStore((s) => s.config.core.allowedResolutions);
  const addResolution = useConfigStore((s) => s.addResolution);
  const removeResolution = useConfigStore((s) => s.removeResolution);
  const [input, setInput] = useState('');

  const handleAdd = (value: string) => {
    const trimmed = value.trim();
    if (trimmed) {
      addResolution(trimmed);
      setInput('');
    }
  };

  const unusedPresets = PRESETS.filter((p) => !resolutions.includes(p));

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Monitor size={16} className="text-[var(--color-accent)]" />
          <h2 className="text-base font-semibold text-[var(--color-text-primary)]">
            Allowed Resolutions
          </h2>
        </div>
        <p className="text-sm text-[var(--color-text-muted)]">
          Define the resolutions permitted in delivery packages (e.g. 1920x1080).
        </p>
      </div>

      {/* Current resolutions */}
      {resolutions.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {resolutions.map((res) => (
            <span
              key={res}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] text-sm font-mono text-[var(--color-text-primary)]"
            >
              {res}
              <button
                onClick={() => removeResolution(res)}
                className="text-[var(--color-text-faint)] hover:text-[var(--color-danger)] transition-colors"
              >
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
      ) : (
        <div className="px-4 py-6 text-center text-sm text-[var(--color-text-faint)] rounded-lg border border-dashed border-[var(--color-border)] bg-[var(--color-surface-1)]">
          No resolutions defined yet.
        </div>
      )}

      {/* Quick presets */}
      {unusedPresets.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-[var(--color-text-faint)]">Quick add:</span>
          {unusedPresets.map((preset) => (
            <button
              key={preset}
              onClick={() => addResolution(preset)}
              className="px-2.5 py-1 rounded border border-dashed border-[var(--color-border)] text-xs font-mono text-[var(--color-text-muted)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] transition-colors"
            >
              + {preset}
            </button>
          ))}
        </div>
      )}

      {/* Custom input */}
      <div className="flex items-center gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Custom resolution (e.g. 2048x1556)"
          className="qc-input flex-1 font-mono"
          onKeyDown={(e) => e.key === 'Enter' && handleAdd(input)}
        />
        <button
          onClick={() => handleAdd(input)}
          disabled={!input.trim()}
          className="qc-btn-primary"
        >
          <Plus size={14} />
          Add
        </button>
      </div>
    </div>
  );
}
