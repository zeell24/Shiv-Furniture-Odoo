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

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />

        <div style={{ padding: 20, flex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/budgets" element={<BudgetManagement />} />
            <Route path="/transactions" element={<TransactionManagement />} />
            <Route path="/reports" element={<ReportViewer />} />
            <Route path="/customer" element={<CustomerDashboard />} />
            <Route path="/customer/invoices" element={<MyInvoices />} />
            <Route path="/customer/payment" element={<PaymentPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
