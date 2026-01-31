export default function TransactionManagement() {
  return (
    <>
      <h2>Transaction Management</h2>

      <input placeholder="Description" style={input} />
      <input placeholder="Amount" style={input} />
      <button style={btn}>Add Transaction</button>
    </>
  );
}

const input = { display: "block", marginBottom: 10, padding: 8 };
const btn = { padding: "8px 15px" };
