import { useState, useEffect } from 'react';
import { FileText, Download, CreditCard, AlertCircle } from 'lucide-react';
import { getTransactions, updateTransaction } from '../../api/services';
import { getAnalyticalAccount } from '../../utils/analyticalEngine';
import { generateInvoicePDF } from '../../utils/pdfgenerate';

const StatusBadge = ({ status }) => {
  const s = status === 'paid' ? 'Paid' : status === 'not_paid' ? 'Not Paid' : 'Partially Paid';
  const styles = {
    Paid: 'bg-green-50 text-green-600 border-green-100',
    'Not Paid': 'bg-red-50 text-red-600 border-red-100',
    'Partially Paid': 'bg-orange-50 text-orange-600 border-orange-100',
  };
  return (
    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${styles[s]}`}>
      {s}
    </span>
  );
};

export default function CustomerDashboard() {
  const [transactions, setTransactions] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getTransactions();
      setTransactions(Array.isArray(res) ? res : []);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePayment = async (id) => {
    try {
      await updateTransaction(id, { status: 'paid' });
      setTransactions((prev) => prev.map((t) => (t.id === id ? { ...t, status: 'paid' } : t)));
      setSelectedTransaction(null);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleDownloadPDF = (inv) => {
    const el = document.getElementById('invoice-table-container');
    if (el) {
      generateInvoicePDF('invoice-table-container', `TXN-${inv.id}`);
    } else {
      alert('Invoice PDF generated for TXN-' + inv.id);
    }
  };

  if (loading) return <div className="p-8">Loading portal...</div>;

  return (
    <div className="animate-in slide-in-from-bottom-6 duration-700">
      <div className="mb-14">
        <h2 className="text-5xl font-black text-slate-900 tracking-tighter">Portal Overview</h2>
        <p className="text-slate-500 mt-2 font-medium">
          Manage your financial commitments and verify production links.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {selectedTransaction ? (
        <div className="max-w-xl mx-auto mt-6 animate-in zoom-in-95 duration-500" id="checkout-view">
          <div className="bg-white rounded-[4rem] shadow-2xl border border-slate-100 p-16 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-2 bg-amber-500" />
            <div className="flex justify-between items-center mb-12">
              <h3 className="text-3xl font-black tracking-tighter">Unified Checkout</h3>
              <button
                onClick={() => setSelectedTransaction(null)}
                className="text-slate-300 hover:text-rose-500 transition-colors uppercase font-black text-[10px] tracking-[0.2em]"
              >
                Close Terminal
              </button>
            </div>
            <div className="bg-slate-50 p-10 rounded-[3rem] mb-12 border border-slate-100 flex justify-between items-center">
              <div>
                <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-3">
                  Total Payable (INR)
                </p>
                <h4 className="text-6xl font-black font-sans tracking-tighter text-slate-900 italic">
                  ₹{(selectedTransaction.amount || 0).toLocaleString('en-IN')}
                </h4>
              </div>
              <div className="w-20 h-20 bg-amber-500 rounded-3xl flex items-center justify-center text-black shadow-lg shadow-amber-500/20">
                <CreditCard size={32} />
              </div>
            </div>
            <div className="space-y-10">
              <div className="space-y-3">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">
                  Card Details
                </label>
                <div className="bg-white border-2 border-slate-100 p-6 rounded-[1.5rem] flex justify-between items-center shadow-inner">
                  <span className="font-black text-lg text-slate-800 tracking-widest font-sans underline decoration-amber-500/50">
                    4242 4242 4242 4242
                  </span>
                  <div className="px-3 py-1 bg-slate-900 rounded text-[9px] text-white font-black uppercase tracking-tighter italic">
                    Stripe Test
                  </div>
                </div>
              </div>
              <div className="flex gap-4 p-6 bg-blue-50/50 rounded-3xl border border-blue-100/50">
                <div className="p-3 bg-blue-500 rounded-xl text-white shrink-0 shadow-lg shadow-blue-500/20">
                  <AlertCircle size={20} />
                </div>
                <p className="text-[11px] text-blue-900 leading-relaxed font-bold italic uppercase tracking-tight">
                  This transaction for &quot;{selectedTransaction.description || '—'}&quot; will be
                  instantly reconciled against the{' '}
                  <span className="text-blue-600">
                    {getAnalyticalAccount(selectedTransaction.description).name}
                  </span>{' '}
                  analytical account.
                </p>
              </div>
              <button
                onClick={() => handlePayment(selectedTransaction.id)}
                className="w-full bg-[#1A1A1A] text-white py-7 rounded-[2.5rem] font-black text-xl shadow-2xl hover:bg-amber-500 hover:text-black hover:-translate-y-1 transition-all active:scale-95 shadow-slate-300"
              >
                Authorize Payment & Reconcile
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6" id="invoice-table-container">
          {transactions.length === 0 ? (
            <div className="bg-white p-16 rounded-[3rem] border border-slate-100 shadow-sm text-center">
              <FileText className="mx-auto text-slate-300 mb-4" size={48} />
              <p className="text-slate-500">No transactions yet. Add transactions from the Transactions page.</p>
            </div>
          ) : (
            transactions.map((inv) => (
              <div
                key={inv.id}
                className="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm flex items-center justify-between hover:shadow-2xl hover:shadow-slate-100 transition-all group"
              >
                <div className="flex items-center gap-10">
                  <div className="w-20 h-20 bg-slate-50 rounded-[2rem] flex items-center justify-center text-slate-300 group-hover:bg-amber-50 group-hover:text-amber-500 transition-all duration-500">
                    <FileText size={32} />
                  </div>
                  <div>
                    <h5 className="font-black text-2xl text-slate-800 tracking-tighter">
                      TXN-{inv.id}
                    </h5>
                    <p className="text-sm font-medium text-slate-400 mt-1">
                      {inv.description || '—'} • {inv.transaction_date || inv.created_at || '—'}
                    </p>
                    <div className="mt-3 inline-flex items-center gap-2 text-[9px] font-bold uppercase tracking-widest text-amber-600 bg-amber-50 px-3 py-1 rounded-full border border-amber-100">
                      Linked: {getAnalyticalAccount(inv.description).name}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-12">
                  <div className="text-right">
                    <p className="text-3xl font-black font-sans tracking-tighter mb-1">
                      ₹{(inv.amount || 0).toLocaleString('en-IN')}
                    </p>
                    <StatusBadge status={inv.status} />
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleDownloadPDF(inv)}
                      className="w-14 h-14 bg-slate-50 hover:bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400 transition-all active:scale-90"
                    >
                      <Download size={22} />
                    </button>
                    {inv.status !== 'paid' && (
                      <button
                        onClick={() => setSelectedTransaction(inv)}
                        className="bg-black text-white px-10 py-4 rounded-[1.5rem] font-black text-sm tracking-tight hover:bg-amber-500 hover:text-black transition-all shadow-xl shadow-slate-200 active:scale-95"
                      >
                        Settle Balance
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
