import { useState, useEffect } from 'react';

/**
 * Custom hook to manage invoice data and payment states
 */
export const useTransactions = (customerId) => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        // In a real app, replace with: await fetch(`/api/invoices/${customerId}`)
        const mockData = [
          { id: 'INV-001', amount: 250.00, status: 'Paid', date: '2023-10-01' },
          { id: 'INV-002', amount: 125.50, status: 'Unpaid', date: '2023-11-15' },
        ];
        setInvoices(mockData);
      } catch (err) {
        setError('Failed to load billing history.');
      } finally {
        setLoading(false);
      }
    };

    if (customerId) fetchInvoices();
  }, [customerId]);

  return { invoices, loading, error };
};