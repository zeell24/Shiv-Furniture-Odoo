import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getTransactions, getMasterBudget } from '../../api/services';

export default function PaymentPage() {
  const [transactions, setTransactions] = useState([]);
  const [masterBudget, setMasterBudget] = useState(1500000);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([getTransactions(), getMasterBudget()])
      .then(([txRes, budgetRes]) => {
        setTransactions(Array.isArray(txRes) ? txRes : []);
        setMasterBudget(budgetRes?.amount ?? 1500000);
      })
      .catch((err) => setError(err.response?.data?.error || err.message))
      .finally(() => setLoading(false));
  }, []);

  const totalActual = transactions.reduce((acc, t) => acc + (t.amount || 0), 0);
  const remaining = masterBudget - totalActual;
  const achievement = masterBudget > 0 ? ((totalActual / masterBudget) * 100).toFixed(1) : 0;

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-4xl">
      <h2 className="text-3xl font-bold mb-2">Payment Overview</h2>
      <p className="text-slate-500 mb-8">Manage payments from the Customer Portal. Settle balances on unpaid transactions.</p>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
          <p className="text-slate-500 text-xs font-bold uppercase mb-2">Actual Expenditure</p>
          <p className="text-2xl font-black text-rose-600">₹{totalActual.toLocaleString('en-IN')}</p>
        </div>
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
          <p className="text-slate-500 text-xs font-bold uppercase mb-2">Remaining Budget</p>
          <p className="text-2xl font-black text-amber-600">₹{remaining.toLocaleString('en-IN')}</p>
        </div>
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
          <p className="text-slate-500 text-xs font-bold uppercase mb-2">Budget Utilization</p>
          <p className="text-2xl font-black">{achievement}%</p>
          <div className="w-full bg-slate-100 h-2 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-amber-500 h-full rounded-full transition-all"
              style={{ width: `${Math.min(achievement, 100)}%` }}
            />
          </div>
        </div>
      </div>

      <p className="mt-8 text-slate-500 text-sm">
        Go to <Link to="/customer" className="text-amber-600 font-bold hover:underline">Customer Portal</Link> to settle unpaid transactions.
      </p>
    </div>
  );
}
