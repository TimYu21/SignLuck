import type { PlateCalculationResult } from '../types/plate';

export interface SearchResponse {
    results: PlateCalculationResult[];
    total_results: number;
    max_probability: number;
}

export async function checkPlate(query: string): Promise<SearchResponse> {
    const response = await fetch('/api/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}