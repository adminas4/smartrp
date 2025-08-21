export interface Material {
    name: string;
    quantity: number;
    unit: string;
    unit_price_nok?: number;
}

export interface WorkflowItem {
    description: string;
    materials: Material[];
}

export interface WorkTimeItem {
    role: string;
    hours: number;
    hourly_rate_nok?: number;
}

export interface CrewItem {
    name: string;
    members: string[];
}

export interface ToolItem {
    name: string;
    quantity: number;
    unit_price_nok?: number;
}

export interface PricelistItem {
    item: string;
    price_nok: number;
}

export interface EstimateResult {
    workflow: WorkflowItem[];
    work_time: WorkTimeItem[];
    crew: CrewItem[];
    tools: ToolItem[];
    pricelist: PricelistItem[];
}