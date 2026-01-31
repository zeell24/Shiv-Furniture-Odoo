// src/pages/customer/MyInvoices.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAnalyticalAccount } from '../../utils/analyticalEngine';

const MyInvoices = () => {
  const [invoices, setInvoices] = useState([
    { id: 'INV-001', date: '2026-01-15', amount: 1500, status: 'Not Paid', product: 'Oak Wood Table' },
    { id: 'INV-002', date: '2026-01-20', amount: 500, status: 'Paid', product: 'Marketing Flyer' }
  ]);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">Shiv Furniture - My Invoices</h1>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost Center (Auto)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {invoices.map((inv) => (
              <tr key={inv.id}>
                <td className="px-6 py-4">{inv.id}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                    {getAnalyticalAccount(inv.product)} {/*  */}
                  </span>
                </td>
                <td className="px-6 py-4">${inv.amount}</td>
                <td className="px-6 py-4">
                  <span className={`font-semibold ${inv.status === 'Paid' ? 'text-green-600' : 'text-red-600'}`}>
                    {inv.status} {/* [cite: 55-59] */}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <Link to={`/invoice/${inv.id}`} className="text-indigo-600 hover:underline">View/Pay</Link>
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