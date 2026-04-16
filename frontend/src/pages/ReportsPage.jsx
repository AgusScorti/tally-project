// src/pages/ReportsPage.jsx
import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import api from '../api/client';
import { motion } from 'framer-motion';

export default function ReportsPage() {
  const [reportData, setReportData] = useState(null);
  const [monthYear, setMonthYear] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReport();
  }, [monthYear]);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const [year, month] = monthYear.split('-');
      const response = await api.get(`/reports/monthly/${year}/${month}`);
      setReportData(response.data);
    } catch (error) {
      console.error('Error fetching report:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !reportData) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <p className="text-tally-text/60">Loading report...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-8"
      >
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-tally-text mb-2">Reports</h1>
          <p className="text-tally-text/60">Analyze your spending patterns</p>
        </div>

        {/* Month Selector */}
        <div className="flex gap-4">
          <input
            type="month"
            value={monthYear}
            onChange={(e) => setMonthYear(e.target.value)}
            className="input-base"
          />
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl p-6 border border-tally-border"
          >
            <p className="text-sm font-medium text-tally-text/60 mb-2">Total spent</p>
            <p className="text-2xl font-bold text-tally-text">${reportData.total_spent}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl p-6 border border-tally-border"
          >
            <p className="text-sm font-medium text-tally-text/60 mb-2">Cards total</p>
            <p className="text-2xl font-bold text-tally-text">${reportData.total_in_cards}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl p-6 border border-tally-border"
          >
            <p className="text-sm font-medium text-tally-text/60 mb-2">Expenses count</p>
            <p className="text-2xl font-bold text-tally-text">
              {reportData.by_category.reduce((sum, cat) => sum + cat.count, 0)}
            </p>
          </motion.div>
        </div>

        {/* By Category */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl border border-tally-border"
        >
          <div className="px-6 py-4 border-b border-tally-border">
            <h2 className="font-semibold text-tally-text">By category</h2>
          </div>
          <div className="divide-y divide-tally-border">
            {reportData.by_category.length > 0 ? (
              reportData.by_category.map((category, idx) => (
                <div
                  key={category.category_id}
                  className="px-6 py-4 hover:bg-tally-hover transition-colors duration-200"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-tally-text">{category.category_name}</p>
                    <p className="font-semibold text-tally-text">${category.total}</p>
                  </div>
                  <div className="w-full bg-tally-border rounded-full h-2">
                    <div
                      className="bg-tally-500 h-2 rounded-full"
                      style={{
                        width: `${(category.total / reportData.total_spent) * 100}%`,
                      }}
                    />
                  </div>
                  <p className="text-xs text-tally-text/60 mt-2">
                    {category.count} expense{category.count !== 1 ? 's' : ''}
                  </p>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-tally-text/60">
                No expenses this month
              </div>
            )}
          </div>
        </motion.div>

        {/* By Card */}
        {reportData.by_card.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl border border-tally-border"
          >
            <div className="px-6 py-4 border-b border-tally-border">
              <h2 className="font-semibold text-tally-text">By card</h2>
            </div>
            <div className="divide-y divide-tally-border">
              {reportData.by_card.map((card) => (
                <div key={card.card_id} className="px-6 py-4 hover:bg-tally-hover transition-colors duration-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-tally-text">{card.card_name}</p>
                      <p className="text-xs text-tally-text/60">{card.count} expenses</p>
                    </div>
                    <p className="font-semibold text-tally-text">${card.total}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    </Layout>
  );
}
