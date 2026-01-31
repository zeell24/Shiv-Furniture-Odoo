import React from 'react';
import { generateInvoicePDF } from '../../utils/pdfgenerate';

export { generateInvoicePDF } from '../../utils/pdfgenerate';

export default function InvoicePDF({ invoice, analyticalAccount }) {
  const handleDownload = () => {
    const id = invoice?.id ?? analyticalAccount;
    generateInvoicePDF('invoice-table-container', invoice?.invoice_number ?? id);
  };

  return (
    <button
      type="button"
      onClick={handleDownload}
      className="text-blue-600 hover:underline text-sm font-semibold"
    >
      Download PDF
    </button>
  );
}
