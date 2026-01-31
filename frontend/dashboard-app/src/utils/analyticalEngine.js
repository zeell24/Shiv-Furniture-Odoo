import React from 'react';
import { Package, Target, Truck, Zap } from 'lucide-react';

const ANALYTICAL_RULES = [
  { keywords: ['wood', 'timber', 'plywood', 'teak', 'oak'], account: 'Production', icon: Package },
  { keywords: ['expo', 'fair', 'advertisement', 'social', 'marketing'], account: 'Marketing', icon: Target },
  { keywords: ['delivery', 'fuel', 'truck', 'shipping', 'freight'], account: 'Logistics', icon: Truck },
  { keywords: ['office', 'stationary', 'rent', 'electricity'], account: 'Administrative', icon: Zap },
];

export function getAnalyticalAccount(productName) {
  if (!productName) return { name: 'General', icon: Zap };
  const input = String(productName).toLowerCase();
  const match = ANALYTICAL_RULES.find((rule) =>
    rule.keywords.some((keyword) => input.includes(keyword))
  );
  if (match) {
    return { name: match.account, icon: match.icon };
  }
  return { name: 'Furniture Expo 2026', icon: Target };
}

export function getAccountName(productName) {
  return getAnalyticalAccount(productName).name;
}
