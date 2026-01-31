import React, { useState, useMemo } from 'react';
import { 
  LayoutDashboard, FileText, CreditCard, Download, 
  ArrowUpRight, Wallet, PieChart, CheckCircle2, 
  Clock, AlertCircle, Search, Edit3, Save, X, 
  Zap, Package, Truck, Target
} from 'lucide-react';

/** * 1. AUTO-ANALYTICAL MODEL ENGINE [cite: 19, 44, 84-85]
 * Rule-based logic to categorize expenses based on keywords.
 */
const ANALYTICAL_RULES = [
  { keywords: ['wood', 'timber', 'plywood', 'teak', 'oak'], account: 'Production', icon: <Package size={14}/> },
  { keywords: ['expo', 'fair', 'advertisement', 'social', 'marketing'], account: 'Marketing', icon: <Target size={14}/> },
  { keywords: ['delivery', 'fuel', 'truck', 'shipping', 'freight'], account: 'Logistics', icon: <Truck size={14}/> },
  { keywords: ['office', 'stationary', 'rent', 'electricity'], account: 'Administrative', icon: <Zap size={14}/> }
];

const getAnalyticalAccount = (productName) => {
  if (!productName) return { name: 'General', icon: <Zap size={14}/> };
  const input = productName.toLowerCase();
  const match = ANALYTICAL_RULES.find(rule => 
    rule.keywords.some(keyword => input.includes(keyword))
  );
  return match ? { name: match.account, icon: match.icon } : { name: 'Furniture Expo 2026', icon: <Target size={14}/> };
};

/**
 * 2. INTEGRATED FRONTEND COMPONENT
 */
export default function ShivFurnitureUnifiedSystem() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  
  // ADMIN BUDGET REVISION STATE [cite: 30]
  const [isEditingBudget, setIsEditingBudget] = useState(false);
  const [approvedBudget, setApprovedBudget] = useState(1500000); // Set in ₹
  const [tempBudget, setTempBudget] = useState(1500000);

  // MASTER DATA: INVOICES & BILLS [cite: 14-18, 46]
  const [invoices, setInvoices] = useState([
    { id: 'SF-26-001', date: '2026-01-10', item: 'A-Grade Teak Wood Log', amount: 125000, status: 'Paid' },
    { id: 'SF-26-002', date: '2026-01-15', item: 'Instagram Ads - Sofa Collection', amount: 45000, status: 'Not Paid' },
    { id: 'SF-26-003', date: '2026-01-22', item: 'Diesel for Surat-Ahmedabad Delivery', amount: 12000, status: 'Partially Paid' },
    { id: 'SF-26-004', date: '2026-01-28', item: 'Marine Plywood Sheets (100 qty)', amount: 280000, status: 'Not Paid' },
  ]);

  // 3. BUDGET vs ACTUAL LOGIC [cite: 27, 49, 81-83]
  const stats = useMemo(() => {
    const totalActual = invoices.reduce((acc, curr) => acc + curr.amount, 0);
    return {
      totalActual,
      remaining: approvedBudget - totalActual,
      achievement: ((totalActual / approvedBudget) * 100).toFixed(1)
    };
  }, [invoices, approvedBudget]);

  // 4. HANDLERS
  const handlePayment = (id) => {
    setInvoices(prev => prev.map(inv => 
      inv.id === id ? { ...inv, status: 'Paid' } : inv // Reconciliation logic [cite: 86-90]
    ));
    alert(`Success: Payment of ₹${selectedInvoice.amount} processed and reconciled with Cost Center.`);
    setActiveTab('invoices');
  };

  const saveBudgetRevision = () => {
    setApprovedBudget(Number(tempBudget));
    setIsEditingBudget(false);
  };

  // UI Components
  const StatusBadge = ({ status }) => {
    const styles = {
      'Paid': 'bg-green-50 text-green-600 border-green-100',
      'Not Paid': 'bg-red-50 text-red-600 border-red-100',
      'Partially Paid': 'bg-orange-50 text-orange-600 border-orange-100'
    };
    return <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${styles[status]}`}>{status}</span>;
  };

  return (
    <div className="flex h-screen bg-[#FDFCFB] text-[#1A1A1A] font-sans selection:bg-amber-100 overflow-hidden">
      
      {/* 5. CREATIVE SIDEBAR WITH LOGO */}
      <aside className="w-80 bg-[#0F0F0F] text-white p-10 flex flex-col shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-200 via-amber-500 to-amber-200"></div>
        
        {/* LOGO AREA */}
        <div className="mb-16 flex items-center gap-4 group cursor-default">
          <div className="w-12 h-12 bg-amber-500 rounded-2xl flex items-center justify-center rotate-3 group-hover:rotate-12 transition-transform duration-500 shadow-lg shadow-amber-500/20">
            <span className="text-black font-black text-2xl">S</span>
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tighter text-white">SHIV <span className="text-amber-500 italic">FURNITURE</span></h1>
            <p className="text-[9px] text-zinc-500 tracking-[0.3em] font-bold uppercase">Heritage ERP v1.0</p>
          </div>
        </div>
        
        <nav className="space-y-3 flex-1">
          <button onClick={() => setActiveTab('dashboard')} className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 ${activeTab === 'dashboard' ? 'bg-amber-500 text-black shadow-xl shadow-amber-500/30' : 'hover:bg-zinc-800/50 text-zinc-400'}`}>
            <LayoutDashboard size={20} /> <span className="font-bold text-sm tracking-tight">Financial Hub</span>
          </button>
          <button onClick={() => setActiveTab('invoices')} className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 ${activeTab === 'invoices' ? 'bg-amber-500 text-black shadow-xl shadow-amber-500/30' : 'hover:bg-zinc-800/50 text-zinc-400'}`}>
            <FileText size={20} /> <span className="font-bold text-sm tracking-tight">Customer Portal</span>
          </button>
        </nav>

        <div className="mt-auto pt-10 border-t border-zinc-800/50 flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 border border-zinc-700 flex items-center justify-center font-bold text-xs">SA</div>
          <div>
            <p className="text-xs font-black uppercase text-amber-500">Admin Account</p>
            <p className="text-[11px] text-zinc-500 font-medium">Surat, Gujarat</p>
          </div>
        </div>
      </aside>

      {/* 6. MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto px-16 py-12 custom-scrollbar">
        
        {/* VIEW: CREATIVE DASHBOARD [cite: 26-30, 68] */}
        {activeTab === 'dashboard' && (
          <div className="animate-in fade-in slide-in-from-top-4 duration-700">
            <header className="flex justify-between items-end mb-12">
              <div>
                <h2 className="text-5xl font-black text-slate-900 tracking-tighter">Business Intelligence</h2>
                <p className="text-slate-500 mt-2 font-medium">Real-time budget monitoring and automated cost-center tracking.</p>
              </div>
              
              {/* ADMIN REVISION [cite: 30] */}
              <div className="flex items-center gap-3">
                {isEditingBudget ? (
                  <div className="flex bg-white p-2 rounded-2xl shadow-xl border border-amber-500 items-center gap-2 scale-105 transition-all">
                    <span className="pl-3 font-black text-amber-600 font-sans">₹</span>
                    <input type="number" value={tempBudget} onChange={(e) => setTempBudget(e.target.value)} className="bg-transparent outline-none px-2 w-32 font-black text-slate-800" />
                    <button onClick={saveBudgetRevision} className="bg-amber-500 p-2.5 rounded-xl text-black hover:bg-amber-400"><Save size={18}/></button>
                  </div>
                ) : (
                  <button onClick={() => { setTempBudget(approvedBudget); setIsEditingBudget(true); }} className="flex items-center gap-3 bg-white px-6 py-4 rounded-2xl shadow-sm border border-slate-100 text-xs font-black text-slate-600 hover:border-amber-500 hover:shadow-lg transition-all uppercase tracking-widest">
                    <Edit3 size={16} className="text-amber-500"/> Revision Budget Master
                  </button>
                )}
              </div>
            </header>

            {/* KEY STATS CARDS */}
            <div className="grid grid-cols-3 gap-10 mb-14">
              <div className="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 relative overflow-hidden group hover:shadow-2xl hover:shadow-slate-200 transition-all">
                <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:scale-110 transition-transform duration-700"><Wallet size={120}/></div>
                <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] mb-4">Master Budget</p>
                <h3 className="text-4xl font-black font-sans leading-none tracking-tighter">₹{approvedBudget.toLocaleString('en-IN')}</h3>
                <div className="flex items-center gap-2 text-emerald-600 font-bold text-xs mt-6 bg-emerald-50 w-fit px-3 py-1 rounded-full">
                  <ArrowUpRight size={14}/> +8.2% Growth
                </div>
              </div>

              <div className="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 relative group overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:scale-110 transition-transform duration-700"><PieChart size={120}/></div>
                <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] mb-4">Actual Expenditure</p>
                <h3 className="text-4xl font-black font-sans leading-none tracking-tighter text-rose-600">₹{stats.totalActual.toLocaleString('en-IN')}</h3>
                <div className="w-full bg-slate-100 h-2 rounded-full mt-6 overflow-hidden">
                  <div className="bg-rose-500 h-full rounded-full transition-all duration-1000" style={{ width: `${stats.achievement}%` }}></div>
                </div>
              </div>

              <div className="bg-[#1A1A1A] p-10 rounded-[3rem] shadow-2xl shadow-slate-300 relative overflow-hidden group">
                <div className="absolute -bottom-4 -right-4 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl group-hover:bg-amber-500/20 transition-all duration-700"></div>
                <p className="text-zinc-500 text-[10px] font-black uppercase tracking-[0.2em] mb-4">Available Capital</p>
                <h3 className="text-4xl font-black font-sans leading-none tracking-tighter text-amber-500">₹{stats.remaining.toLocaleString('en-IN')}</h3>
                <div className="mt-6 flex items-center gap-2">
                  <div className="flex -space-x-2">
                    {[1, 2, 3].map(i => <div key={i} className="w-6 h-6 rounded-full border-2 border-[#1A1A1A] bg-zinc-700"></div>)}
                  </div>
                  <span className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase">Verified by Finance</span>
                </div>
              </div>
            </div>

            {/* AUDIT TABLE */}
            <div className="flex items-center justify-between mb-8">
              <h4 className="text-2xl font-black tracking-tight flex items-center gap-3">
                <Clock className="text-amber-500" size={24} /> Recent Audit Log
              </h4>
              <div className="bg-slate-100 p-2 rounded-xl flex items-center gap-2 px-4 text-slate-400">
                <Search size={16} />
                <input type="text" placeholder="Filter Transactions..." className="bg-transparent outline-none text-xs font-bold" />
              </div>
            </div>
            
            <div className="bg-white rounded-[2.5rem] border border-slate-100 overflow-hidden shadow-sm">
              <table className="w-full text-left">
                <thead className="bg-slate-50/50 border-b border-slate-100">
                  <tr>
                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">Transaction ID</th>
                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">Analytical Account (Auto)</th>
                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">Amount</th>
                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-400">Settlement</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {invoices.map(inv => {
                    const account = getAnalyticalAccount(inv.item);
                    return (
                      <tr key={inv.id} className="hover:bg-slate-50/50 transition-colors group">
                        <td className="p-8">
                          <div className="font-black text-slate-800 tracking-tight">{inv.item}</div>
                          <div className="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-tighter">{inv.id} • {inv.date}</div>
                        </td>
                        <td className="p-8">
                          <div className="flex items-center gap-2 bg-slate-100 w-fit px-4 py-1.5 rounded-lg border border-slate-200 group-hover:border-amber-500/30 transition-colors">
                             <span className="text-amber-600">{account.icon}</span>
                             <span className="text-[10px] font-black tracking-widest uppercase text-slate-700">{account.name}</span>
                          </div>
                        </td>
                        <td className="p-8 font-black text-slate-900 font-sans tracking-tight">₹{inv.amount.toLocaleString('en-IN')}</td>
                        <td className="p-8"><StatusBadge status={inv.status} /></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* VIEW: CUSTOMER PORTAL [cite: 31-35, 61-65] */}
        {activeTab === 'invoices' && (
          <div className="animate-in slide-in-from-bottom-6 duration-700">
            <div className="mb-14">
              <h2 className="text-5xl font-black text-slate-900 tracking-tighter">Portal Overview</h2>
              <p className="text-slate-500 mt-2 font-medium">Manage your financial commitments and verify production links.</p>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {invoices.map(inv => (
                <div key={inv.id} className="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm flex items-center justify-between hover:shadow-2xl hover:shadow-slate-100 transition-all group">
                  <div className="flex items-center gap-10">
                    <div className="w-20 h-20 bg-slate-50 rounded-[2rem] flex items-center justify-center text-slate-300 group-hover:bg-amber-50 group-hover:text-amber-500 transition-all duration-500">
                      <FileText size={32} />
                    </div>
                    <div>
                      <h5 className="font-black text-2xl text-slate-800 tracking-tighter">{inv.id}</h5>
                      <p className="text-sm font-medium text-slate-400 mt-1">{inv.item} • {inv.date}</p>
                      <div className="mt-3 inline-flex items-center gap-2 text-[9px] font-bold uppercase tracking-widest text-amber-600 bg-amber-50 px-3 py-1 rounded-full border border-amber-100">
                        Linked: {getAnalyticalAccount(inv.item).name}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-12">
                    <div className="text-right">
                      <p className="text-3xl font-black font-sans tracking-tighter mb-1">₹{inv.amount.toLocaleString('en-IN')}</p>
                      <StatusBadge status={inv.status} />
                    </div>
                    <div className="flex gap-3">
                      <button onClick={() => alert("Invoice PDF Generated Successfully")} className="w-14 h-14 bg-slate-50 hover:bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400 transition-all active:scale-90">
                        <Download size={22} />
                      </button>
                      {inv.status !== 'Paid' && (
                        <button 
                          onClick={() => { setSelectedInvoice(inv); setActiveTab('checkout'); }}
                          className="bg-black text-white px-10 py-4 rounded-[1.5rem] font-black text-sm tracking-tight hover:bg-amber-500 hover:text-black transition-all shadow-xl shadow-slate-200 active:scale-95"
                        >
                          Settle Balance
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* VIEW: STRIPE-STYLE CHECKOUT [cite: 65, 90] */}
        {activeTab === 'checkout' && selectedInvoice && (
          <div className="max-w-xl mx-auto mt-6 animate-in zoom-in-95 duration-500">
            <div className="bg-white rounded-[4rem] shadow-2xl border border-slate-100 p-16 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-2 bg-amber-500"></div>
              
              <div className="flex justify-between items-center mb-12">
                <h3 className="text-3xl font-black tracking-tighter">Unified Checkout</h3>
                <button onClick={() => setActiveTab('invoices')} className="text-slate-300 hover:text-rose-500 transition-colors uppercase font-black text-[10px] tracking-[0.2em]">Close Terminal</button>
              </div>

              <div className="bg-slate-50 p-10 rounded-[3rem] mb-12 border border-slate-100 flex justify-between items-center">
                <div>
                  <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-3">Total Payable (INR)</p>
                  <h4 className="text-6xl font-black font-sans tracking-tighter text-slate-900 italic">₹{selectedInvoice.amount.toLocaleString('en-IN')}</h4>
                </div>
                <div className="w-20 h-20 bg-amber-500 rounded-3xl flex items-center justify-center text-black shadow-lg shadow-amber-500/20">
                  <CreditCard size={32} />
                </div>
              </div>

              <div className="space-y-10">
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Card Details</label>
                  <div className="bg-white border-2 border-slate-100 p-6 rounded-[1.5rem] flex justify-between items-center shadow-inner group-focus-within:border-amber-500 transition-colors">
                    <span className="font-black text-lg text-slate-800 tracking-widest font-sans underline decoration-amber-500/50">4242 4242 4242 4242</span>
                    <div className="px-3 py-1 bg-slate-900 rounded text-[9px] text-white font-black uppercase tracking-tighter italic">Stripe Test</div>
                  </div>
                </div>
                
                <div className="flex gap-4 p-6 bg-blue-50/50 rounded-3xl border border-blue-100/50">
                  <div className="p-3 bg-blue-500 rounded-xl text-white shrink-0 shadow-lg shadow-blue-500/20"><AlertCircle size={20} /></div>
                  <p className="text-[11px] text-blue-900 leading-relaxed font-bold italic uppercase tracking-tight">
                    This transaction for "{selectedInvoice.item}" will be instantly reconciled against the 
                    <span className="text-blue-600"> {getAnalyticalAccount(selectedInvoice.item).name} </span> analytical account.
                  </p>
                </div>

                <button 
                  onClick={() => handlePayment(selectedInvoice.id)}
                  className="w-full bg-[#1A1A1A] text-white py-7 rounded-[2.5rem] font-black text-xl shadow-2xl hover:bg-amber-500 hover:text-black hover:-translate-y-1 transition-all active:scale-95 shadow-slate-300"
                >
                  Authorize Payment & Reconcile
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}