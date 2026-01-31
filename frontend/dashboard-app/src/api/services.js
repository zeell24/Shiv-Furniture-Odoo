import api from './api';

export async function getChartData() {
  const { data } = await api.get('/reports/chart-data');
  return data;
}

export async function getMasterBudget() {
  const { data } = await api.get('/budgets/master');
  return data;
}

export async function updateMasterBudget(amount) {
  const { data } = await api.put('/budgets/master', { amount });
  return data;
}

export async function getTransactions(params = {}) {
  const { data } = await api.get('/transactions/', { params });
  return data;
}

export async function createTransaction(payload) {
  const { data } = await api.post('/transactions/', payload);
  return data;
}

export async function updateTransaction(id, payload) {
  const { data } = await api.put(`/transactions/${id}`, payload);
  return data;
}

export async function getCostCenters() {
  const { data } = await api.get('/cost-centers/');
  return data;
}

export async function getBudgets() {
  const { data } = await api.get('/budgets/');
  return data;
}

export async function createBudget(payload) {
  const { data } = await api.post('/budgets/', payload);
  return data;
}

export async function getBudgetVsActual() {
  const { data } = await api.get('/reports/budget-vs-actual');
  return data;
}
