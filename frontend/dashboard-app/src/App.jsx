import { useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login.jsx";
import SignUp from "./pages/SignUp.jsx";
import Dashboard from "./pages/admin/Dashboard.jsx";
import BudgetManagement from "./pages/admin/BudgetManagement.jsx";
import TransactionManagement from "./pages/admin/TransactionManagement.jsx";
import ReportViewer from "./pages/admin/ReportViewer.jsx";
import MyInvoices from "./pages/customer/invoice.jsx";
import PaymentPage from "./pages/customer/payment.jsx";
import CustomerDashboard from "./pages/customer/customerdashboard.jsx";

import Navbar from "./components/common/Navbar.jsx";
import Sidebar from "./components/common/Sidebar.jsx";
import { AuthContext } from "./context/AuthContext";

function AppContent() {
  const { user, loading } = useContext(AuthContext);
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-[#FDFCFB]">
        <div className="text-slate-600 font-medium">Loading...</div>
      </div>
    );
  }
  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }
  return (
    <>
      <Navbar />
      <div className="flex min-h-screen bg-[#FDFCFB]">
        <Sidebar />
        <main className="flex-1 overflow-y-auto px-16 py-12">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/budgets" element={<BudgetManagement />} />
            <Route path="/transactions" element={<TransactionManagement />} />
            <Route path="/reports" element={<ReportViewer />} />
            <Route path="/customer" element={<CustomerDashboard />} />
            <Route path="/customer/invoices" element={<MyInvoices />} />
            <Route path="/customer/payment" element={<PaymentPage />} />
            <Route path="/login" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
