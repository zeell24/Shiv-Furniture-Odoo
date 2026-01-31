import { useState } from "react";

export default function TransactionForm() {
  const [desc, setDesc] = useState("");
  const [amount, setAmount] = useState("");

  return (
    <>
      <input className="form-control mb-2" placeholder="Description"
        onChange={e => setDesc(e.target.value)} />
      <input className="form-control mb-2" placeholder="Amount"
        onChange={e => setAmount(e.target.value)} />
      <button className="btn btn-primary">
        Add Transaction
      </button>
    </>
  );
}
