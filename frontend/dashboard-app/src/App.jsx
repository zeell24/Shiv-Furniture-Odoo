import { useContext } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

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
  const { loading } = useContext(AuthContext);
  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <div>Loading...</div>
      </div>
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
