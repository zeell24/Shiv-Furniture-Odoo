import React from 'react';
import { useTransactions } from '../../hooks/useTransactions';
import { generateInvoicePDF } from '../../components/invoices/InvoicePDF';

const MyInvoices = () => {
  const { invoices, loading } = useTransactions('user_123');

  if (loading) return <div className="p-8 text-center">Loading your billing history...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Billing History</h1>
      <div id="invoice-table-container" className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="p-4">Invoice ID</th>
              <th className="p-4">Date</th>
              <th className="p-4">Amount</th>
              <th className="p-4">Status</th>
              <th className="p-4">Action</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id} className="border-b hover:bg-gray-50 transition">
                <td className="p-4 font-medium">{inv.id}</td>
                <td className="p-4 text-gray-600">{inv.date}</td>
                <td className="p-4">${inv.amount.toFixed(2)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs ${inv.status === 'Paid' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {inv.status}
                  </span>
                </td>
                <td className="p-4">
                  <button 
                    onClick={() => generateInvoicePDF('invoice-table-container', inv.id)}
                    className="text-blue-600 hover:underline text-sm font-semibold"
                  >
                    Download PDF
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MyInvoices;