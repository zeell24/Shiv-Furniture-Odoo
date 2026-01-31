import React from 'react';
import { useTransactions } from '../../hooks/useTransactions';
import { getAnalyticalAccount } from '../../utils/analyticalEngine';

const CustomerDashboard = () => {
  const { invoices, stats } = useTransactions([
    { id: 'SF-001', item: 'Premium Teak Wood', amount: 50000, status: 'Paid' },
    { id: 'SF-002', item: 'Facebook Ads - Sofa', amount: 15000, status: 'Not Paid' }
  ]);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-8">Shiv Furniture Dashboard</h1>
      
      {/* Budget Summary [cite: 27, 28] */}
      <div className="grid grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-6 rounded-xl shadow border-l-4 border-amber-500">
          <p className="text-sm text-gray-500">Total Budget utilized</p>
          <p className="text-2xl font-bold">₹{stats.actual}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow border-l-4 border-green-500">
          <p className="text-sm text-gray-500">Remaining Balance</p>
          <p className="text-2xl font-bold">₹{stats.remaining}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow border-l-4 border-blue-500">
          <p className="text-sm text-gray-500">Achievement %</p>
          <p className="text-2xl font-bold">{stats.achievement}%</p>
        </div>
      </div>

      {/* Transaction List [cite: 46, 47] */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-4">Item</th>
              <th className="p-4">Cost Center (Auto)</th>
              <th className="p-4">Amount</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map(inv => (
              <tr key={inv.id} className="border-t">
                <td className="p-4 font-medium">{inv.item}</td>
                <td className="p-4">
                  <span className="px-2 py-1 bg-gray-200 rounded text-xs">
                    {getAnalyticalAccount(inv.item)}
                  </span>
                </td>
                <td className="p-4 font-bold">₹{inv.amount}</td>
                <td className="p-4 text-xs font-bold uppercase">{inv.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CustomerDashboard;