import { useState, useMemo } from 'react';

export const useTransactions = (initialInvoices) => {
  const [invoices, setInvoices] = useState(initialInvoices);
  const [budgetLimit, setBudgetLimit] = useState(1500000); // Admin configurable budget [cite: 48]

  const stats = useMemo(() => {
    const actual = invoices.reduce((acc, inv) => acc + inv.amount, 0);
    return {
      actual,
      remaining: budgetLimit - actual,
      achievement: ((actual / budgetLimit) * 100).toFixed(1)
    };
  }, [invoices, budgetLimit]);

  const updatePaymentStatus = (id, status) => {
    setInvoices(prev => prev.map(inv => inv.id === id ? { ...inv, status } : inv));
  };

  return { invoices, stats, updatePaymentStatus, setBudgetLimit };
};