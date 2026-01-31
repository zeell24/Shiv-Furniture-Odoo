import { useState } from "react";

export default function BudgetForm() {
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");

  const submit = () => {
    alert(`Budget Added: ${name} - ${amount}`);
  };

  return (
    <div className="mb-3">
      <input className="form-control mb-2" placeholder="Budget Name"
        onChange={e => setName(e.target.value)} />
      <input className="form-control mb-2" placeholder="Amount"
        onChange={e => setAmount(e.target.value)} />
      <button className="btn btn-success" onClick={submit}>Add Budget</button>
    </div>
  );
}
