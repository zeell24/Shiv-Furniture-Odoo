import { getAnalyticalAccount } from '../utils/analyticalEngine';

describe('Auto-Analytical Model Test Suite', () => {
  test('should link "Teak Wood" to Production', () => {
    expect(getAnalyticalAccount('Teak Wood')).toBe('Production');
  });

  test('should link "Instagram Marketing" to Marketing', () => {
    expect(getAnalyticalAccount('Instagram Marketing')).toBe('Marketing');
  });

  test('should fallback to Furniture Expo 2026 for unknown items', () => {
    expect(getAnalyticalAccount('Random Item')).toBe('Furniture Expo 2026');
  });
});