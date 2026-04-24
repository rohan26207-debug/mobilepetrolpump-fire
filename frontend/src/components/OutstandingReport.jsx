import React, { useMemo } from 'react';
import { Card, CardContent } from './ui/card';
import { FileText } from 'lucide-react';

const OutstandingReport = ({ customers, creditData, payments, isDarkMode }) => {
  // Calculate outstanding for each customer
  const outstandingReport = useMemo(() => {
    return customers.map(customer => {
      const totalCredit = creditData
        .filter(c => c.customerName === customer.name)
        .reduce((sum, c) => sum + c.amount, 0);

      const totalReceived = payments
        .filter(p => p.customerId === customer.id)
        .reduce((sum, p) => sum + p.amount, 0);

      const outstanding = totalCredit - totalReceived;

      return {
        id: customer.id,
        name: customer.name,
        outstanding,
      };
    })
      .filter(r => r.outstanding !== 0)
      .sort((a, b) => b.outstanding - a.outstanding);
  }, [customers, creditData, payments]);

  const totalOutstanding = useMemo(() => {
    return outstandingReport.reduce((sum, r) => sum + r.outstanding, 0);
  }, [outstandingReport]);

  // Shared B&W cell styles (match Reports / Bank Settlement tab look)
  const thBase = `px-2 py-1 border text-xs font-bold ${
    isDarkMode ? 'border-gray-600 bg-gray-800 text-white' : 'border-slate-400 bg-slate-100 text-slate-800'
  }`;
  const tdBase = `px-2 py-1 border text-xs ${
    isDarkMode ? 'border-gray-600 text-gray-200' : 'border-slate-400 text-slate-800'
  }`;
  const rowZebra = (i) =>
    i % 2 === 1
      ? (isDarkMode ? 'bg-gray-800' : 'bg-slate-50')
      : (isDarkMode ? 'bg-gray-700' : 'bg-white');
  const totalRowCls = isDarkMode ? 'bg-gray-900' : 'bg-slate-200';
  const totalCellCls = `px-2 py-1 border text-xs font-bold ${
    isDarkMode ? 'border-gray-600 text-white' : 'border-slate-400 text-slate-900'
  }`;

  return (
    <Card className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'} shadow-lg`}>
      <CardContent className="p-2 sm:p-3 space-y-3">
        <h2 className={`text-lg sm:text-2xl font-bold mb-2 ${
          isDarkMode ? 'text-white' : 'text-slate-800'
        }`}>
          Outstanding Report
        </h2>

        {outstandingReport.length === 0 ? (
          <div className={`text-center py-8 ${isDarkMode ? 'text-gray-400' : 'text-slate-500'}`}>
            <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No outstanding balances</p>
            <p className="text-sm mt-1">All customers have cleared their dues</p>
          </div>
        ) : (
          <>
            {/* Summary Table */}
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className={`${thBase} text-left`} colSpan={2}>Summary</th>
                </tr>
                <tr>
                  <th className={`${thBase} text-left`}>Metric</th>
                  <th className={`${thBase} text-right`}>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr className={rowZebra(0)}>
                  <td className={tdBase}>Customers with Outstanding</td>
                  <td className={`${tdBase} text-right font-mono`}>{outstandingReport.length}</td>
                </tr>
                <tr className={totalRowCls}>
                  <td className={totalCellCls}>Total Outstanding (₹)</td>
                  <td className={`${totalCellCls} text-right font-mono`}>{totalOutstanding.toFixed(2)}</td>
                </tr>
              </tbody>
            </table>

            {/* Details Table */}
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className={`${thBase} text-left`} colSpan={3}>Customer Outstanding</th>
                  </tr>
                  <tr>
                    <th className={`${thBase} text-center`}>#</th>
                    <th className={`${thBase} text-left`}>Customer Name</th>
                    <th className={`${thBase} text-right`}>Outstanding (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  {outstandingReport.map((row, i) => (
                    <tr key={row.id} className={rowZebra(i)}>
                      <td className={`${tdBase} text-center`}>{i + 1}</td>
                      <td className={tdBase}>{row.name}</td>
                      <td className={`${tdBase} text-right font-mono`}>{row.outstanding.toFixed(2)}</td>
                    </tr>
                  ))}
                  <tr className={totalRowCls}>
                    <td className={totalCellCls} colSpan={2}>TOTAL</td>
                    <td className={`${totalCellCls} text-right font-mono`}>{totalOutstanding.toFixed(2)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className={`text-xs p-2 rounded border ${
              isDarkMode ? 'border-gray-600 bg-gray-700 text-gray-300' : 'border-slate-300 bg-slate-50 text-slate-700'
            }`}>
              <strong className={isDarkMode ? 'text-white' : 'text-slate-800'}>Note:</strong> Positive balance = customer owes you. Negative balance = you owe the customer.
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default OutstandingReport;
