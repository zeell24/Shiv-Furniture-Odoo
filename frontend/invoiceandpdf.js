import React from 'react';

const InvoicePDF = ({ invoice, analyticalAccount }) => {
  const handleDownload = () => {
    console.log(`Generating PDF for ${invoice.id}...`);
    alert(`Downloading PDF for ${invoice.id}\nLinked Cost Center: ${analyticalAccount}`);
  };

  return (
    <button onClick={handleDownload} className="flex items-center gap-2 text-blue-600 hover:underline">
      Download Invoice (PDF)
    </button>
  );
};

export default InvoicePDF;