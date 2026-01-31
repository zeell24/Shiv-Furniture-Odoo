import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div style={{
      width: 220,
      background: "#111827",
      minHeight: "100vh",
      padding: 20
    }}>
      <Link style={linkStyle} to="/">Dashboard</Link>
      <Link style={linkStyle} to="/budgets">Budgets</Link>
      <Link style={linkStyle} to="/transactions">Transactions</Link>
      <Link style={linkStyle} to="/reports">Reports</Link>
    </div>
  );
}

const linkStyle = {
  display: "block",
  color: "white",
  textDecoration: "none",
  marginBottom: 15
};
