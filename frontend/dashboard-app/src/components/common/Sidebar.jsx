import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  Wallet,
  CreditCard,
  BarChart3,
  Users,
  Receipt,
  DollarSign,
} from "lucide-react";

export default function Sidebar() {
  const location = useLocation();

  const linkClass = (path) =>
    `w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 ${
      location.pathname === path
        ? "bg-amber-500 text-black shadow-xl shadow-amber-500/30"
        : "hover:bg-zinc-800/50 text-zinc-400"
    }`;

  return (
    <aside className="w-80 bg-[#0F0F0F] text-white p-10 flex flex-col shadow-2xl relative min-h-screen">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-200 via-amber-500 to-amber-200" />
      <div className="mb-16 flex items-center gap-4 group cursor-default">
        <div className="w-12 h-12 bg-amber-500 rounded-2xl flex items-center justify-center rotate-3 group-hover:rotate-12 transition-transform duration-500 shadow-lg shadow-amber-500/20">
          <span className="text-black font-black text-2xl">S</span>
        </div>
        <div>
          <h1 className="text-xl font-black tracking-tighter text-white">
            SHIV <span className="text-amber-500 italic">FURNITURE</span>
          </h1>
          <p className="text-[9px] text-zinc-500 tracking-[0.3em] font-bold uppercase">
            Heritage ERP v1.0
          </p>
        </div>
      </div>
      <nav className="space-y-3 flex-1">
        <Link to="/" className={linkClass("/")}>
          <LayoutDashboard size={20} />
          <span className="font-bold text-sm tracking-tight">Financial Hub</span>
        </Link>
        <Link to="/transactions" className={linkClass("/transactions")}>
          <CreditCard size={20} />
          <span className="font-bold text-sm tracking-tight">Transactions</span>
        </Link>
        <Link to="/budgets" className={linkClass("/budgets")}>
          <Wallet size={20} />
          <span className="font-bold text-sm tracking-tight">Budgets</span>
        </Link>
        <Link to="/reports" className={linkClass("/reports")}>
          <BarChart3 size={20} />
          <span className="font-bold text-sm tracking-tight">Reports</span>
        </Link>
        <Link to="/customer" className={linkClass("/customer")}>
          <FileText size={20} />
          <span className="font-bold text-sm tracking-tight">Customer Portal</span>
        </Link>
        <Link to="/customer/invoices" className={linkClass("/customer/invoices")}>
          <Receipt size={20} />
          <span className="font-bold text-sm tracking-tight">My Invoices</span>
        </Link>
        <Link to="/customer/payment" className={linkClass("/customer/payment")}>
          <DollarSign size={20} />
          <span className="font-bold text-sm tracking-tight">Payment</span>
        </Link>
      </nav>
      <div className="mt-auto pt-10 border-t border-zinc-800/50 flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 border border-zinc-700 flex items-center justify-center font-bold text-xs">
          SA
        </div>
        <div>
          <p className="text-xs font-black uppercase text-amber-500">Admin Account</p>
          <p className="text-[11px] text-zinc-500 font-medium">Surat, Gujarat</p>
        </div>
      </div>
    </aside>
  );
}
