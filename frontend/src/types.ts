// ─── Core Types ────────────────────────────────────────────────────────────────

export interface PlotSpec {
  length: number;
  width:  number;
}

export interface RoomRequirements {
  bedrooms:         number;
  bathrooms:        number;
  kitchen:          number;
  living_dining:    number;
  parking:          number;
  balcony:          number;
  garden:           boolean;
  home_office:      boolean;
  pooja_prayer_room: boolean;
}

export type BudgetTier        = 'economy' | 'standard' | 'premium' | 'luxury';
export type ArchitecturalStyle = 'modern' | 'contemporary' | 'traditional' | 'colonial' | 'mediterranean' | 'minimalist' | 'indo-fusion';
export type ClimateLocation   = 'tropical' | 'temperate' | 'arid' | 'cold' | 'coastal';
export type CulturalPreference = 'vastu' | 'feng_shui' | 'qibla' | 'contemporary' | 'none';

export interface DesignRequirement {
  plot:                 PlotSpec;
  floors:               number;
  rooms:                RoomRequirements;
  budget:               BudgetTier;
  architectural_style:  ArchitecturalStyle;
  climate_location:     ClimateLocation;
  cultural_preference:  CulturalPreference;
  accessibility:        boolean;
  future_expansion:     boolean;
  priority?:            'space_efficiency' | 'flow' | 'light' | 'privacy' | 'balanced';
}

// ─── Room & Design ─────────────────────────────────────────────────────────────

export interface RoomSpec {
  id:         string;
  name:       string;
  type:       string;
  x:          number;
  y:          number;
  width:      number;
  height:     number;
  floor:      number;
  area_sqft?: number;
}

export interface QualityScores {
  space_efficiency: number;
  natural_light:    number;
  privacy_score:    number;
  circulation_flow: number;
  vastu_score:      number;
  overall_score:    number;
}

export interface CostBreakdownItem {
  category:   string;
  amount:     number;
  percentage: number;
}

export interface CostEstimateData {
  total_estimated_cost: number;
  rate_per_sqft:        number;
  built_up_area_sqft:   number;
  budget_tier:          string;
  currency_symbol:      string;
  breakdown:            CostBreakdownItem[];
  disclaimer:           string;
}

export interface CulturalEvaluationData {
  preference:         string;
  overall_score:      number;
  compliance_label:   string;
  recommendations:    string[];
  room_scores:        { room: string; score: number; note: string }[];
}

export interface CandidateDesign {
  design_id:            string;
  candidate_index:      number;
  rooms:                RoomSpec[];
  floors:               number;
  total_built_up_area:  number;
  quality_scores:       QualityScores;
  constraint_satisfied: boolean;
  pareto_rank:          number;
  architectural_style:  string;
  cost_estimate?:       CostEstimateData;
  cultural_evaluation?: CulturalEvaluationData;
}

// ─── API Responses ─────────────────────────────────────────────────────────────

export interface GenerateDesignsResponse {
  status:       string;
  requirements: Record<string, unknown>;
  designs:      CandidateDesign[];
}

export interface WhatIfResult {
  modified_rooms:    RoomSpec[];
  changes_applied:   string[];
  quality_delta:     Record<string, number>;
  new_cost_estimate: CostEstimateData;
}

// ─── Analytics & Benchmark ───────────────────────────────────────────────────

export interface ModelHistoryItem {
  version:       string;
  deployed_at:   string;
  accuracy:      number;
  f1_score:      number;
  validity_rate: number;
  status:        string;
}

export interface AnalyticsData {
  total_generated_designs: number;
  accepted_designs:        number;
  rejected_designs:        number;
  avg_space_utilization:   number;
  avg_cost_inr:            string;
  avg_design_score:        number;
  most_requested_rooms:    string[];
  popular_styles:          string[];
  active_model_version:    string;
  model_history:           ModelHistoryItem[];
  feedback_count:          number;
}

export interface EvaluationBenchmarkItem {
  model:             string;
  validity_rate:     string;
  space_utilization: string;
  requirement_match: string;
  mae_score:         string;
  f1_score:          string;
  latency_ms:        string;
}

