import { useState, useEffect } from 'react';
import { getBudgets, createBudget, getCostCenters } from '../../api/services';
import api from '../../api/api';

export default function BudgetManagement() {
  const [budgets, setBudgets] = useState([]);
  const [costCenters, setCostCenters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    cost_center_id: '',
    amount: '',
    period_start: new Date().toISOString().slice(0, 7) + '-01',
    period_end: new Date().toISOString().slice(0, 7) + '-28',
  });

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [budgetRes, ccRes] = await Promise.all([getBudgets(), getCostCenters()]);
      setBudgets(Array.isArray(budgetRes) ? budgetRes : []);
      setCostCenters(Array.isArray(ccRes) ? ccRes : []);
      if (costCenters.length && !form.cost_center_id) {
        setForm((f) => ({ ...f, cost_center_id: ccRes[0]?.id || '' }));
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (costCenters.length && !form.cost_center_id) {
      setForm((f) => ({ ...f, cost_center_id: costCenters[0]?.id || '' }));
    }
  }, [costCenters]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.cost_center_id || !form.amount || Number(form.amount) <= 0) {
      setError('Cost center and amount are required.');
      return;
    }
    try {
      await createBudget({
        cost_center_id: Number(form.cost_center_id),
        amount: Number(form.amount),
        period_start: form.period_start,
        period_end: form.period_end,
      });
      setForm({
        cost_center_id: costCenters[0]?.id || '',
        amount: '',
        period_start: new Date().toISOString().slice(0, 7) + '-01',
        period_end: new Date().toISOString().slice(0, 7) + '-28',
      });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this budget?')) return;
    try {
      await api.delete(`/budgets/${id}`);
      setBudgets((prev) => prev.filter((b) => b.id !== id));
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Budget Management</h2>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm mb-10 max-w-2xl"
      >
        <h3 className="text-lg font-bold mb-6">Add Budget</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-slate-600 mb-2">Cost Center</label>
            <select
              value={form.cost_center_id}
              onChange={(e) => setForm({ ...form, cost_center_id: e.target.value })}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
              required
            >
              <option value="">Select...</option>
              {costCenters.map((cc) => (
                <option key={cc.id} value={cc.id}>
                  {cc.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-600 mb-2">Amount (₹)</label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="500000"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-600 mb-2">Period Start</label>
            <input
              type="date"
              value={form.period_start}
              onChange={(e) => setForm({ ...form, period_start: e.target.value })}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-600 mb-2">Period End</label>
            <input
              type="date"
              value={form.period_end}
              onChange={(e) => setForm({ ...form, period_end: e.target.value })}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
            />
          </div>
        </div>
        <button
          type="submit"
          className="mt-6 bg-amber-500 text-black px-8 py-3 rounded-xl font-bold hover:bg-amber-400 transition-colors"
        >
          Add Budget
        </button>
      </form>

      <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Cost Center</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Amount</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Period</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Actual Spent</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Utilization</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {budgets.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-slate-500 text-center">
                  No budgets yet. Add one above. Run seed script if cost centers are empty.
                </td>
              </tr>
            ) : (
              budgets.map((b) => (
                <tr key={b.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-medium">{b.cost_center_name || '—'}</td>
                  <td className="p-4 font-bold">₹{(b.amount || 0).toLocaleString('en-IN')}</td>
                  <td className="p-4 text-slate-600">
                    {b.period_start} to {b.period_end}
                  </td>
                  <td className="p-4">₹{(b.actual_spent || 0).toLocaleString('en-IN')}</td>
                  <td className="p-4">
                    <span className={b.utilization_percentage >= 90 ? 'text-red-600 font-bold' : ''}>
                      {b.utilization_percentage ?? 0}%
                    </span>
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => handleDelete(b.id)}
                      className="text-red-600 text-xs hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
