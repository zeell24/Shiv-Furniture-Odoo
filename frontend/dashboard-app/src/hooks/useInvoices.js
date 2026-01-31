import { useState, useEffect } from 'react';
import api from '../api/api';

/**
 * Fetch invoices from backend API. Use with AuthContext token when available.
 */
export function useInvoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .get('/invoices/')
      .then((res) => {
        if (!cancelled && res.data) {
          const list = Array.isArray(res.data) ? res.data : res.data.invoices || [];
          setInvoices(list.map((inv) => ({
            id: inv.id,
            invoice_number: inv.invoice_number,
            date: inv.created_at || inv.due_date,
            amount: inv.amount ?? 0,
            status: inv.status === 'paid' ? 'Paid' : inv.status === 'partial' ? 'Partial' : 'Unpaid',
            ...inv
          })));
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.response?.data?.error || err.message);
          setInvoices([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return { invoices, loading, error };
}
