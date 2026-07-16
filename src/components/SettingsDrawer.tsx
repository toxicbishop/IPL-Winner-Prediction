import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sliders, RefreshCw, Loader2 } from 'lucide-react';

interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const WEIGHT_LABELS = [
  'Squad Strength Base',
  'Recent Form (3 YR)',
  'Pure Machine Learning',
  'Historical Playoff Rate',
];

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ isOpen, onClose }) => {
  const [rebuilding, setRebuilding] = useState(false);

  const handleRebuild = async () => {
    setRebuilding(true);
    try {
      await fetch(`${API_BASE}/api/trigger-pipeline`, { method: 'POST' });
      setTimeout(() => setRebuilding(false), 3000);
    } catch (err) {
      console.error(err);
      setRebuilding(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="drawer-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="drawer-panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween', duration: 0.2, ease: 'easeOut' }}
          >
            <div className="drawer-header">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                <Sliders size={16} strokeWidth={1.5} /> Platform Settings
              </h2>
              <button
                onClick={onClose}
                style={{
                  background: 'none',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-muted)',
                  cursor: 'pointer',
                  width: 28,
                  height: 28,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <X size={14} strokeWidth={1.5} />
              </button>
            </div>

            {/* Bayesian Weights */}
            <div className="drawer-section">
              <h3>Bayesian Priors Weights</h3>
              <p>Adjust the influence of each domain on the final output signal.</p>

              {WEIGHT_LABELS.map(label => (
                <div key={label} style={{ marginBottom: 'var(--space-md)' }}>
                  <div style={{
                    display: 'flex', justifyContent: 'space-between',
                    fontSize: '0.6875rem', marginBottom: 'var(--space-xs)',
                    fontFamily: 'var(--font-mono)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: 'var(--color-text-muted)',
                  }}>
                    <span>{label}</span>
                    <span style={{ color: 'var(--color-primary)' }}>0.25</span>
                  </div>
                  <input type="range" min="0" max="100" defaultValue="25" disabled />
                </div>
              ))}

              <button className="btn-ghost" style={{ width: '100%', marginTop: 'var(--space-md)' }} disabled>
                Recalculate Bounds
              </button>
            </div>

            {/* Pipeline Controller */}
            <div className="drawer-section">
              <h3>Pipeline Controller</h3>
              <p>Trigger a hard rebuild of the entire ensemble cluster.</p>

              <button
                className="btn-primary"
                style={{ width: '100%' }}
                onClick={handleRebuild}
                disabled={rebuilding}
              >
                {rebuilding ? (
                  <>
                    <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                    Rebuilding...
                  </>
                ) : (
                  <>
                    <RefreshCw size={14} strokeWidth={1.75} />
                    Force Pipeline Rebuild
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default SettingsDrawer;
