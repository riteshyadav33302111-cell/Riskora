import { useState, useCallback, useRef } from 'react';
import { scanUrl } from '../utils/api';

/**
 * Custom hook to manage URL scanning state and logic.
 */
export function useUrlScanner() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scanPhase, setScanPhase] = useState('idle'); // idle | validating | scanning | done

  const abortRef = useRef(null);

  const validate = useCallback((inputUrl) => {
    if (!inputUrl.trim()) return 'Please enter a URL.';
    if (!inputUrl.match(/^https?:\/\//i))
      return 'URL must start with http:// or https://';
    if (inputUrl.length > 2048)
      return 'URL is too long (max 2048 characters).';
    return null;
  }, []);

  const scan = useCallback(async (inputUrl) => {
    const validationError = validate(inputUrl);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setResult(null);
    setIsLoading(true);
    setScanPhase('validating');

    // Brief simulated "validating" phase for UX
    await new Promise((r) => setTimeout(r, 400));
    setScanPhase('scanning');

    try {
      const data = await scanUrl(inputUrl);
      setResult(data);
      setScanPhase('done');
    } catch (err) {
      setError(err.message || 'Scan failed. Please try again.');
      setScanPhase('idle');
    } finally {
      setIsLoading(false);
    }
  }, [validate]);

  const reset = useCallback(() => {
    setUrl('');
    setResult(null);
    setError(null);
    setIsLoading(false);
    setScanPhase('idle');
  }, []);

  return { url, setUrl, result, isLoading, error, scanPhase, scan, reset };
}
