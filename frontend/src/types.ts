export type Material = {
  name?: string;
  qty?: number;
  unit?: string;
};

export type WorkflowItem = {
  task?: string;
  hours?: number;
};

export type CrewMember = {
  role?: string;
  count?: number;
};

export type Tool = {
  name?: string;
  days?: number;
};

export type AnalyserResponse = {
  materials: Material[];
  workflow: WorkflowItem[];
  crew: CrewMember[];
  tools: Tool[];
};

export type PricingParams = {
  labor_rate: number;       // NOK/h
  material_markup: number;  // 0.15 = +15%
  overhead_pct: number;     // 0.10 = +10%
  profit_pct: number;       // 0.10 = +10%
  currency: string;
};

export type RecalcResponse = {
  lines: {
    materials: number;
    labor: number;
    tools: number;
    overhead: number;
    profit: number;
  };
  total: number;
  currency: string;
};

// Patogumui UI rodymui
export type Totals = {
  materials: number;
  labor: number;
  tools: number;
  overhead: number;
  profit: number;
  total: number;
  currency: string;
};
