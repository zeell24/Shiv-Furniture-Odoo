// src/utils/analyticalEngine.js

const ANALYTICAL_RULES = [
  { keywords: ['wood', 'timber', 'plywood'], account: 'Production' },
  { keywords: ['expo', 'fair', 'advertisement', 'social media'], account: 'Marketing' },
  { keywords: ['delivery', 'fuel', 'truck'], account: 'Logistics' },
  { keywords: ['office', 'stationary', 'rent'], account: 'Administrative' }
];

/**
 * Auto-Analytical Model Rule Engine 
 * Categorizes expenses based on keywords in product names or descriptions.
 */
export const getAnalyticalAccount = (productName) => {
  if (!productName) return 'General';
  
  const normalizedInput = productName.toLowerCase();
  
  for (const rule of ANALYTICAL_RULES) {
    if (rule.keywords.some(keyword => normalizedInput.includes(keyword))) {
      return rule.account;
    }
  }
  
  return 'Uncategorized'; // Default if no match found [cite: 47]
};