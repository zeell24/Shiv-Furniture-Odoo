import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';
import { Download, FileText, PieChart } from 'lucide-react';
import { getBudgetVsActual, getChartData } from '../../api/services';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function ReportViewer() {
  const [report, setReport] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [reportRes, chartRes] = await Promise.all([
        getBudgetVsActual(),
        getChartData(),
      ]);
      setReport(reportRes);
      setChartData(chartRes);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDownload = () => {
    if (!report) return;
    const summary = report.summary || {};
    const details = report.details || [];
    const text = [
      'SHIV FURNITURE - BUDGET VS ACTUAL REPORT',
      'Generated: ' + new Date().toISOString(),
      '',
      'SUMMARY',
      `Total Budget: ₹${(summary.total_budget || 0).toLocaleString('en-IN')}`,
      `Total Actual: ₹${(summary.total_actual || 0).toLocaleString('en-IN')}`,
      `Variance: ₹${(summary.total_variance || 0).toLocaleString('en-IN')}`,
      `Utilization: ${summary.overall_utilization || 0}%`,
      '',
      'DETAILS BY COST CENTER',
      ...details.map(
        (d) =>
          `${d.cost_center_name || '—'}: Budget ₹${(d.budget_amount || 0).toLocaleString('en-IN')} | Actual ₹${(d.actual_spent || 0).toLocaleString('en-IN')} | ${d.utilization_percentage || 0}%`
      ),
    ].join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shiv-furniture-report-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="p-8">Loading report...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold">Reports</h2>
          <p className="text-slate-500 mt-1">Budget vs actual and expense reports from database.</p>
        </div>
        <button
          onClick={handleDownload}
          disabled={!report}
          className="flex items-center gap-2 bg-amber-500 text-black px-6 py-3 rounded-xl font-bold hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download size={18} /> Download Report
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {report?.summary && (
        <div className="grid grid-cols-4 gap-4 mb-10">
          <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <p className="text-slate-500 text-xs font-bold uppercase mb-2">Total Budget</p>
            <p className="text-2xl font-black">₹{(report.summary.total_budget || 0).toLocaleString('en-IN')}</p>
          </div>
          <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <p className="text-slate-500 text-xs font-bold uppercase mb-2">Total Actual</p>
            <p className="text-2xl font-black text-rose-600">₹{(report.summary.total_actual || 0).toLocaleString('en-IN')}</p>
          </div>
          <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <p className="text-slate-500 text-xs font-bold uppercase mb-2">Variance</p>
            <p className="text-2xl font-black">₹{(report.summary.total_variance || 0).toLocaleString('en-IN')}</p>
          </div>
          <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <p className="text-slate-500 text-xs font-bold uppercase mb-2">Utilization</p>
            <p className="text-2xl font-black">{report.summary.overall_utilization || 0}%</p>
          </div>
        </div>
      )}

      {/* Chart - only when data exists */}
      <div className="mb-10">
        <h3 className="text-lg font-bold mb-4">Expense Chart</h3>
        {chartData?.has_data && chartData?.labels?.length > 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm h-80">
            <Bar
              data={{
                labels: chartData.labels,
                datasets: chartData.datasets || [],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: { y: { beginAtZero: true } },
              }}
            />
          </div>
        ) : (
          <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl p-12 text-center">
            <PieChart className="mx-auto text-slate-300 mb-4" size={48} />
            <p className="text-slate-500">No transaction data. Add transactions to see the report chart.</p>
          </div>
        )}
      </div>

      {report?.details && report.details.length > 0 ? (
        <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm">
          <h3 className="p-6 text-lg font-bold border-b border-slate-100">Budget vs Actual by Cost Center</h3>
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="p-4 text-left text-xs font-bold text-slate-600">Cost Center</th>
                <th className="p-4 text-left text-xs font-bold text-slate-600">Budget</th>
                <th className="p-4 text-left text-xs font-bold text-slate-600">Actual Spent</th>
                <th className="p-4 text-left text-xs font-bold text-slate-600">Variance</th>
                <th className="p-4 text-left text-xs font-bold text-slate-600">Utilization</th>
              </tr>
            </thead>
            <tbody>
              {report.details.map((d) => (
                <tr key={d.budget_id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-medium">{d.cost_center_name || '—'}</td>
                  <td className="p-4">₹{(d.budget_amount || 0).toLocaleString('en-IN')}</td>
                  <td className="p-4">₹{(d.actual_spent || 0).toLocaleString('en-IN')}</td>
                  <td className="p-4">₹{(d.variance || 0).toLocaleString('en-IN')}</td>
                  <td className={`p-4 font-bold ${(d.utilization_percentage || 0) >= 90 ? 'text-red-600' : ''}`}>
                    {d.utilization_percentage ?? 0}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl p-12 text-center">
          <FileText className="mx-auto text-slate-300 mb-4" size={48} />
          <p className="text-slate-500">No budget data. Add budgets from the Budgets page.</p>
        </div>
      )}
    </div>
  );
}
