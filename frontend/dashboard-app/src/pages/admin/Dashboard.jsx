import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale);

export default function Dashboard() {
  const data = {
    labels: ["Jan", "Feb", "Mar"],
    datasets: [{
      label: "Expenses",
      data: [1200, 900, 1400],
      backgroundColor: "#3b82f6"
    }]
  };

  return (
    <>
      <h2>Dashboard</h2>
      <Bar data={data} />
    </>
  );
}
