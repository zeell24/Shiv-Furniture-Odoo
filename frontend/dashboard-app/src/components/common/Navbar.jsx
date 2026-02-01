import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="bg-[#0F0F0F] text-white px-8 py-4 flex items-center justify-between border-b border-zinc-800">
      <div className="flex items-center gap-4">
        <span className="font-black text-lg tracking-tight">SHIV FURNITURE</span>
        <span className="text-zinc-500 text-sm">Heritage ERP</span>
        {user?.role && (
          <span className="text-[10px] uppercase tracking-wider text-amber-500 font-bold bg-amber-500/10 px-2 py-1 rounded">
            {user.role}
          </span>
        )}
      </div>
      <button
        type="button"
        onClick={handleLogout}
        className="text-xs font-bold text-zinc-400 hover:text-white uppercase tracking-wider transition-colors"
      >
        Sign out
      </button>
    </div>
  );
}
