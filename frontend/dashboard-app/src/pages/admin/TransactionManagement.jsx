import { useState, useEffect } from 'react';
import { getAnalyticalAccount } from '../../utils/analyticalEngine';
import {
  getTransactions,
  createTransaction,
  getCostCenters,
  updateTransaction,
} from '../../api/services';
import api from '../../api/api';

export default function TransactionManagement() {
  const [transactions, setTransactions] = useState([]);
  const [costCenters, setCostCenters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    description: '',
    amount: '',
    transaction_date: new Date().toISOString().slice(0, 10),
    type: 'purchase',
    status: 'not_paid',
  });

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [txRes, ccRes] = await Promise.all([getTransactions(), getCostCenters()]);
      setTransactions(Array.isArray(txRes) ? txRes : []);
      setCostCenters(Array.isArray(ccRes) ? ccRes : []);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const suggestedAccount = getAnalyticalAccount(form.description);
  const suggestedCostCenter = costCenters.find(
    (cc) => cc.name.toLowerCase() === suggestedAccount.name.toLowerCase()
  );
  const costCenterId = suggestedCostCenter?.id || costCenters[0]?.id;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.description.trim() || !form.amount || Number(form.amount) <= 0) {
      setError('Description and amount are required.');
      return;
    }
    if (!costCenterId) {
      setError('No cost center found. Run seed script to create cost centers.');
      return;
    }
    try {
      await createTransaction({
        type: form.type || 'purchase',
        amount: Number(form.amount),
        cost_center_id: costCenterId,
        transaction_date: form.transaction_date,
        description: form.description.trim(),
        status: form.status || 'not_paid',
      });
      setForm({ description: '', amount: '', transaction_date: new Date().toISOString().slice(0, 10), type: 'purchase', status: 'not_paid' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await updateTransaction(id, { status });
      setTransactions((prev) => prev.map((t) => (t.id === id ? { ...t, status } : t)));
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this transaction?')) return;
    try {
      await api.delete(`/transactions/${id}`);
      setTransactions((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Transaction Management</h2>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm mb-10 max-w-2xl"
      >
        <h3 className="text-lg font-bold mb-6">Add Transaction</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-600 mb-2">Description / Item</label>
            <input
              placeholder="e.g. A-Grade Teak Wood Log, Instagram Ads..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            />
            {form.description && (
              <p className="mt-2 text-xs text-slate-500">
                Auto-categorized as: <span className="font-bold text-amber-600">{suggestedAccount.name}</span>
              </p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-600 mb-2">Amount (₹)</label>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="125000"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-600 mb-2">Date</label>
              <input
                type="date"
                value={form.transaction_date}
                onChange={(e) => setForm({ ...form, transaction_date: e.target.value })}
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
              />
            </div>
          </div>
          <div className="flex gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-600 mb-2">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
              >
                <option value="purchase">Purchase / Expense</option>
                <option value="sale">Sale</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-600 mb-2">Status</label>
              <select
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                className="px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500"
              >
                <option value="not_paid">Not Paid</option>
                <option value="partially_paid">Partially Paid</option>
                <option value="paid">Paid</option>
              </select>
            </div>
          </div>
        </div>
        <button
          type="submit"
          className="mt-6 bg-amber-500 text-black px-8 py-3 rounded-xl font-bold hover:bg-amber-400 transition-colors"
        >
          Add Transaction
        </button>
      </form>

      <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm">
        <h3 className="p-6 text-lg font-bold border-b border-slate-100">All Transactions</h3>
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Description</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Cost Center</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Amount</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Date</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Status</th>
              <th className="p-4 text-left text-xs font-bold text-slate-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-slate-500 text-center">
                  No transactions yet. Add one above.
                </td>
              </tr>
            ) : (
              transactions.map((t) => (
                <tr key={t.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-medium">{t.description || '—'}</td>
                  <td className="p-4 text-slate-600">{t.cost_center_name || '—'}</td>
                  <td className="p-4 font-bold">₹{(t.amount || 0).toLocaleString('en-IN')}</td>
                  <td className="p-4 text-slate-600">{t.transaction_date || '—'}</td>
                  <td className="p-4">
                    <select
                      value={t.status || 'paid'}
                      onChange={(e) => handleStatusChange(t.id, e.target.value)}
                      className="text-xs border rounded px-2 py-1"
                    >
                      <option value="paid">Paid</option>
                      <option value="not_paid">Not Paid</option>
                      <option value="partially_paid">Partially Paid</option>
                    </select>
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => handleDelete(t.id)}
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
