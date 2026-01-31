import { useState, useEffect, useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';
import {
  LayoutDashboard,
  FileText,
  CreditCard,
  Download,
  ArrowUpRight,
  Wallet,
  PieChart,
  Clock,
  Search,
  Edit3,
  Save,
  Zap,
  Package,
  Truck,
  Target,
} from 'lucide-react';
import { getChartData, getMasterBudget, updateMasterBudget, getTransactions, updateTransaction } from '../../api/services';
import { getAnalyticalAccount } from '../../utils/analyticalEngine';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

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

export default function Dashboard() {
  const [chartData, setChartData] = useState(null);
  const [masterBudget, setMasterBudget] = useState(1500000);
  const [transactions, setTransactions] = useState([]);
  const [isEditingBudget, setIsEditingBudget] = useState(false);
  const [tempBudget, setTempBudget] = useState(1500000);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterQuery, setFilterQuery] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [chartRes, budgetRes, txRes] = await Promise.all([
        getChartData(),
        getMasterBudget(),
        getTransactions(),
      ]);
      setChartData(chartRes);
      setMasterBudget(budgetRes.amount ?? 1500000);
      setTempBudget(budgetRes.amount ?? 1500000);
      setTransactions(Array.isArray(txRes) ? txRes : []);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const stats = useMemo(() => {
    const totalActual = transactions.reduce((acc, t) => acc + (t.amount || 0), 0);
    return {
      totalActual,
      remaining: masterBudget - totalActual,
      achievement: masterBudget > 0 ? ((totalActual / masterBudget) * 100).toFixed(1) : '0',
    };
  }, [transactions, masterBudget]);

  const filteredTransactions = useMemo(() => {
    if (!filterQuery.trim()) return transactions;
    const q = filterQuery.toLowerCase();
    return transactions.filter(
      (t) =>
        (t.description || '').toLowerCase().includes(q) ||
        (t.cost_center_name || '').toLowerCase().includes(q)
    );
  }, [transactions, filterQuery]);

  const handleSaveBudget = async () => {
    try {
      await updateMasterBudget(Number(tempBudget));
      setMasterBudget(tempBudget);
      setIsEditingBudget(false);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleMarkPaid = async (id) => {
    try {
      await updateTransaction(id, { status: 'paid' });
      setTransactions((prev) =>
        prev.map((t) => (t.id === id ? { ...t, status: 'paid' } : t))
      );
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-slate-500">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="animate-in fade-in slide-in-from-top-4 duration-700">
      <header className="flex justify-between items-end mb-12">
        <div>
          <h2 className="text-5xl font-black text-slate-900 tracking-tighter">
            Business Intelligence
          </h2>
          <p className="text-slate-500 mt-2 font-medium">
            Real-time budget monitoring and automated cost-center tracking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {isEditingBudget ? (
            <div className="flex bg-white p-2 rounded-2xl shadow-xl border border-amber-500 items-center gap-2 scale-105 transition-all">
              <span className="pl-3 font-black text-amber-600 font-sans">₹</span>
              <input
                type="number"
                value={tempBudget}
                onChange={(e) => setTempBudget(e.target.value)}
                className="bg-transparent outline-none px-2 w-32 font-black text-slate-800"
              />
              <button
                onClick={handleSaveBudget}
                className="bg-amber-500 p-2.5 rounded-xl text-black hover:bg-amber-400"
              >
                <Save size={18} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => {
                setTempBudget(masterBudget);
                setIsEditingBudget(true);
              }}
              className="flex items-center gap-3 bg-white px-6 py-4 rounded-2xl shadow-sm border border-slate-100 text-xs font-black text-slate-600 hover:border-amber-500 hover:shadow-lg transition-all uppercase tracking-widest"
            >
              <Edit3 size={16} className="text-amber-500" /> Revision Budget Master
            </button>
          )}
        </div>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-3 gap-10 mb-14">
        <div className="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 relative overflow-hidden group hover:shadow-2xl hover:shadow-slate-200 transition-all">
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
            <Wallet size={120} />
          </div>
          <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] mb-4">
            Master Budget
          </p>
          <h3 className="text-4xl font-black font-sans leading-none tracking-tighter">
            ₹{Number(masterBudget).toLocaleString('en-IN')}
          </h3>
          <div className="flex items-center gap-2 text-emerald-600 font-bold text-xs mt-6 bg-emerald-50 w-fit px-3 py-1 rounded-full">
            <ArrowUpRight size={14} /> +8.2% Growth
          </div>
        </div>

        <div className="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 relative group overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
            <PieChart size={120} />
          </div>
          <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] mb-4">
            Actual Expenditure
          </p>
          <h3 className="text-4xl font-black font-sans leading-none tracking-tighter text-rose-600">
            ₹{stats.totalActual.toLocaleString('en-IN')}
          </h3>
          <div className="w-full bg-slate-100 h-2 rounded-full mt-6 overflow-hidden">
            <div
              className="bg-rose-500 h-full rounded-full transition-all duration-1000"
              style={{ width: `${Math.min(stats.achievement, 100)}%` }}
            />
          </div>
        </div>

        <div className="bg-[#1A1A1A] p-10 rounded-[3rem] shadow-2xl shadow-slate-300 relative overflow-hidden group">
          <div className="absolute -bottom-4 -right-4 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl group-hover:bg-amber-500/20 transition-all duration-700" />
          <p className="text-zinc-500 text-[10px] font-black uppercase tracking-[0.2em] mb-4">
            Available Capital
          </p>
          <h3 className="text-4xl font-black font-sans leading-none tracking-tighter text-amber-500">
            ₹{stats.remaining.toLocaleString('en-IN')}
          </h3>
          <div className="mt-6 flex items-center gap-2">
            <div className="flex -space-x-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="w-6 h-6 rounded-full border-2 border-[#1A1A1A] bg-zinc-700"
                />
              ))}
            </div>
            <span className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase">
              Verified by Finance
            </span>
          </div>
        </div>
      </div>

      {/* Chart - only when data exists */}
      <div className="mb-14">
        <h4 className="text-2xl font-black tracking-tight mb-6">Expense Report</h4>
        {chartData?.has_data && chartData?.labels?.length > 0 ? (
          <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm h-80">
            <Bar
              data={{
                labels: chartData.labels,
                datasets: chartData.datasets || [],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'top' },
                },
                scales: {
                  y: { beginAtZero: true },
                },
              }}
            />
          </div>
        ) : (
          <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-[2.5rem] p-16 text-center">
            <PieChart className="mx-auto text-slate-300 mb-4" size={64} />
            <p className="text-slate-500 font-medium">
              No transaction data yet. Add transactions to see the expense chart.
            </p>
            <p className="text-slate-400 text-sm mt-2">
              Go to Transactions to add your first expense.
            </p>
          </div>
        )}
      </div>

      {/* Audit Table */}
      <div className="flex items-center justify-between mb-8">
        <h4 className="text-2xl font-black tracking-tight flex items-center gap-3">
          <Clock className="text-amber-500" size={24} /> Recent Audit Log
        </h4>
        <div className="bg-slate-100 p-2 rounded-xl flex items-center gap-2 px-4 text-slate-400">
          <Search size={16} />
          <input
            type="text"
            placeholder="Filter Transactions..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="bg-transparent outline-none text-xs font-bold"
          />
        </div>
      </div>

      <div className="bg-white rounded-[2.5rem] border border-slate-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-slate-50/50 border-b border-slate-100">
            <tr>
              <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">
                Transaction ID
              </th>
              <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">
                Analytical Account (Auto)
              </th>
              <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">
                Amount
              </th>
              <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">
                Settlement
              </th>
              <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredTransactions.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-8 text-slate-500 text-center">
                  No transactions yet. Add transactions from the Transactions page.
                </td>
              </tr>
            ) : (
              filteredTransactions.map((t) => {
                const account = getAnalyticalAccount(t.description || '');
                const Icon = account.icon;
                return (
                  <tr key={t.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="p-8">
                      <div className="font-black text-slate-800 tracking-tight">
                        {t.description || '—'}
                      </div>
                      <div className="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-tighter">
                        TXN-{t.id} • {t.transaction_date || t.created_at || '—'}
                      </div>
                    </td>
                    <td className="p-8">
                      <div className="flex items-center gap-2 bg-slate-100 w-fit px-4 py-1.5 rounded-lg border border-slate-200 group-hover:border-amber-500/30 transition-colors">
                        <span className="text-amber-600">
                          <Icon size={14} />
                        </span>
                        <span className="text-[10px] font-black tracking-widest uppercase text-slate-700">
                          {t.cost_center_name || account.name}
                        </span>
                      </div>
                    </td>
                    <td className="p-8 font-black text-slate-900 font-sans tracking-tight">
                      ₹{(t.amount || 0).toLocaleString('en-IN')}
                    </td>
                    <td className="p-8">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="p-8">
                      {t.status !== 'paid' && (
                        <button
                          onClick={() => handleMarkPaid(t.id)}
                          className="text-xs font-bold text-amber-600 hover:text-amber-700 uppercase"
                        >
                          Mark Paid
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
