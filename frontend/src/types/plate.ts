export interface PlateVisualSymbol {
    value: string;
    is_fixed: boolean;
    possible_query_indices: number[];
}

export interface PlateCalculationResult {
    country_name: string;
    country_code: string;
    lat: number;
    lng: number;
    probability: number;
    symbols: PlateVisualSymbol[];
    allowed_letters: string;
    pattern: string;
    flag_emoji?: string;
    examples: string[];
}

export interface SearchRequest {
    query: string;
}
