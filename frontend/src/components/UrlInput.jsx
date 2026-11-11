import { useState } from 'react';
import { Search, X, Loader2, AlertCircle } from 'lucide-react';

export default function UrlInput({ url, setUrl, onScan, isLoading, error }) {
  const [focused, setFocused] = useState(false);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      onScan(url);
    }
  };

  const handleClear = () => {
    setUrl('');
  };

  return (
    <div className="w-full space-y-3">
      {/* Input row */}
      <div
        className={`relative flex items-center rounded-xl border transition-all duration-200 ${
          focused
            ? 'border-violet-500/60 shadow-lg shadow-violet-500/10'
            : error
            ? 'border-red-500/40'
            : 'border-white/15'
        } bg-navy-900/80`}
      >
        {/* Search icon */}
        <div className="pl-4 pr-2 flex-shrink-0">
          <Search className="w-4 h-4 text-slate-400" />
        </div>

        {/* URL input */}
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="https://example.com/page?query=value"
          className="flex-1 bg-transparent py-3.5 text-white placeholder-slate-500 font-mono text-sm focus:outline-none"
          disabled={isLoading}
          autoComplete="off"
          spellCheck={false}
        />

        {/* Clear button */}
        {url && !isLoading && (
          <button
            onClick={handleClear}
            className="px-2 text-slate-500 hover:text-slate-300 transition-colors"
            aria-label="Clear URL"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        {/* Scan button */}
        <button
          onClick={() => onScan(url)}
          disabled={isLoading || !url.trim()}
          className={`m-1.5 px-5 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 flex items-center gap-2 ${
            isLoading || !url.trim()
              ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white shadow-md hover:shadow-violet-500/25 active:scale-95'
          }`}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Scanning…
            </>
          ) : (
            <>
              <Search className="w-3.5 h-3.5" />
              Scan URL
            </>
          )}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-2 text-red-400 text-sm animate-fade-in">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Helper text */}
      {!error && (
        <p className="text-xs text-slate-500 pl-1">
          Enter a full URL including the protocol (http:// or https://). 
          Press Enter or click Scan to analyse.
        </p>
      )}
    </div>
  );
}
