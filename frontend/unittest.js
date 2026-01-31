/**
 * Auto-Analytical Model Rule Engine [cite: 19, 85]
 * Automatically links transactions to analytical accounts based on product keywords.
 */
const RULES = [
  { keywords: ['wood', 'timber', 'oak', 'plywood', 'teak'], account: 'Production' },
  { keywords: ['expo', 'fair', 'advertisement', 'social', 'marketing'], account: 'Marketing' },
  { keywords: ['delivery', 'fuel', 'truck', 'logistics'], account: 'Logistics' },
  { keywords: ['office', 'rent', 'electricity', 'stationary'], account: 'Administrative' }
];

export const getAnalyticalAccount = (productName) => {
  if (!productName) return 'General';
  const input = productName.toLowerCase();
  const match = RULES.find(rule => rule.keywords.some(k => input.includes(k)));
  
  // Returns account name or default as per Business Logic [cite: 80, 85]
  return match ? match.account : 'Furniture Expo 2026'; 
};