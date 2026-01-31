/**
 * Generate invoice as PDF. Uses browser print when jsPDF/html2canvas are not installed.
 * To use real PDF generation, add: npm i jspdf html2canvas
 * and use the optional implementation below.
 */
export async function generateInvoicePDF(elementId, invoiceNumber) {
  const element = document.getElementById(elementId);
  if (!element) {
    console.warn('Invoice element not found:', elementId);
    return;
  }
  // Use browser print for the invoice section (no extra deps)
  const prevTitle = document.title;
  document.title = `Invoice_${invoiceNumber || 'export'}`;
  const printContent = element.innerHTML;
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(`
      <!DOCTYPE html><html><head><title>Invoice ${invoiceNumber || ''}</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      </head><body>${printContent}</body></html>
    `);
    printWindow.document.close();
    printWindow.print();
    printWindow.close();
  } else {
    // Fallback: print whole page
    window.print();
  }
  document.title = prevTitle;
}
