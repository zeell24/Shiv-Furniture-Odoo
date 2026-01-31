import React, { useState, useMemo } from 'react';

export const useTransactions = (initialInvoices = []) => {
  const [invoices, setInvoices] = useState(initialInvoices);
  const [budgetLimit, setBudgetLimit] = useState(1500000);

  const stats = useMemo(() => {
    const actual = invoices.reduce((acc, inv) => acc + (inv.amount || 0), 0);
    return {
      actual,
      remaining: budgetLimit - actual,
      achievement: budgetLimit > 0 ? ((actual / budgetLimit) * 100).toFixed(1) : 0
    };
  }, [invoices, budgetLimit]);

  const updatePaymentStatus = (id, status) => {
    setInvoices(prev => prev.map(inv => (inv.id === id ? { ...inv, status } : inv)));
  };

  return { invoices, stats, updatePaymentStatus, setBudgetLimit };
};

export default function PaymentPage() {
  const { stats } = useTransactions([]);
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Payment</h1>
      <p className="text-gray-600 mb-4">Manage payments and view payment history from the Invoices page.</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <p className="text-sm text-gray-500">Actual</p>
          <p className="text-xl font-semibold">₹{stats.actual?.toLocaleString() ?? 0}</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <p className="text-sm text-gray-500">Remaining</p>
          <p className="text-xl font-semibold">₹{stats.remaining?.toLocaleString() ?? 0}</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <p className="text-sm text-gray-500">Achievement %</p>
          <p className="text-xl font-semibold">{stats.achievement ?? 0}%</p>
        </div>
      </div>
    </div>
  );
}
