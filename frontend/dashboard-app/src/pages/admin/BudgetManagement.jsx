export default function BudgetManagement() {
  return (
    <>
      <h2>Budget Management</h2>

      <input placeholder="Budget Name" style={input} />
      <input placeholder="Amount" style={input} />
      <button style={btn}>Add Budget</button>

      <table style={table}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Marketing</td>
            <td>5000</td>
          </tr>
        </tbody>
      </table>
    </>
  );
}

const input = { display: "block", marginBottom: 10, padding: 8 };
const btn = { padding: "8px 15px", marginBottom: 20 };
const table = { width: "100%", borderCollapse: "collapse" };
