import React, { useState } from 'react';
import { analyzeEstimate, recalculateEstimate } from './api';
import { EstimateResult } from './types';

const EstimateDemo: React.FC = () => {
    const [description, setDescription] = useState('');
    const [estimateResult, setEstimateResult] = useState<EstimateResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleAnalyze = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await analyzeEstimate(description, {});
            setEstimateResult(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleRecalculate = async () => {
        if (!estimateResult) return;
        setLoading(true);
        setError(null);
        try {
            const result = await recalculateEstimate(estimateResult);
            setEstimateResult(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Estimate Analysis</h1>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
            <button onClick={handleAnalyze} disabled={loading}>Analyze</button>
            {loading && <p>Loading...</p>}
            {error && <p>Error: {error}</p>}
            {estimateResult && (
                <div>
                    <h2>Estimate Result</h2>
                    <pre>{JSON.stringify(estimateResult, null, 2)}</pre>
                    <button onClick={handleRecalculate} disabled={loading}>Recalculate</button>
                </div>
            )}
        </div>
    );
};

export default EstimateDemo;