import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

interface ErrorBannerProps {
  message?: string | null;
  onRetry: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => (
  <div className="api-error-banner">
    <div className="api-error-copy">
      <AlertTriangle size={18} strokeWidth={1.5} />
      <div>
        <div className="mono-label api-error-title">Data stream interrupted</div>
        <p>{message || 'One or more API widgets could not refresh.'}</p>
      </div>
    </div>
    <button className="btn-ghost api-retry-button" onClick={onRetry}>
      <RotateCcw size={14} strokeWidth={1.75} />
      Retry
    </button>
  </div>
);

export const WidgetSkeleton: React.FC<{ rows?: number; height?: number }> = ({ rows = 3, height = 28 }) => (
  <div className="widget-skeleton-stack">
    {[...Array(rows)].map((_, i) => (
      <div key={i} className="skeleton" style={{ height }} />
    ))}
  </div>
);
