import { EstimateResult } from './types';

export async function analyzeEstimate(description: string, customFields?: Record<string, any>): Promise<EstimateResult> {
    const response = await fetch('/api/estimate/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description, custom_fields: customFields }),
    });
    if (!response.ok) {
        throw new Error('Failed to analyze estimate');
    }
    return response.json();
}

export async function recalculateEstimate(result: EstimateResult): Promise<EstimateResult> {
    const response = await fetch('/api/estimate/recalculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(result),
    });
    if (!response.ok) {
        throw new Error('Failed to recalculate estimate');
    }
    return response.json();
}