import UrlInput from '../components/UrlInput';
import ScanningAnimation from '../components/ScanningAnimation';
import ScanResult from '../components/ScanResult';
import { useUrlScanner } from '../hooks/useUrlScanner';
import { Search } from 'lucide-react';

export default function ScannerPage() {
  const { url, setUrl, result, isLoading, error, scanPhase, scan, reset } = useUrlScanner();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="section-heading flex items-center gap-2">
          <Search className="w-6 h-6 text-violet-400" />
          URL Scanner
        </h2>
        <p className="section-subheading">
          Enter any URL to receive a phishing risk assessment with explainable indicators.
        </p>
      </div>

      {/* Input (always visible for quick re-scan) */}
      <UrlInput
        url={url}
        setUrl={setUrl}
        onScan={scan}
        isLoading={isLoading}
        error={error}
      />

      {/* Scanning animation */}
      {(scanPhase === 'validating' || scanPhase === 'scanning') && (
        <ScanningAnimation phase={scanPhase} />
      )}

      {/* Result */}
      {result && scanPhase === 'done' && (
        <ScanResult result={result} onNewScan={reset} />
      )}
    </div>
  );
}
