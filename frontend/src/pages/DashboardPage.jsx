// src/pages/DashboardPage.jsx
import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import api from '../api/client';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [recentExpenses, setRecentExpenses] = useState([]);
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, expensesRes, debtsRes] = await Promise.all([
        api.get('/reports/statistics'),
        api.get('/expenses?limit=5'),
        api.get('/payments/me/owe'),
      ]);

      setStats(statsRes.data);
      setRecentExpenses(expensesRes.data);
      setDebts(debtsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <Layout>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="space-y-8"
      >
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-tally-text mb-2">Dashboard</h1>
          <p className="text-tally-text/60">Overview of your spending</p>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <motion.div variants={itemVariants} className="bg-white rounded-xl p-6 border border-tally-border">
              <p className="text-sm font-medium text-tally-text/60 mb-2">Total spent</p>
              <p className="text-2xl font-bold text-tally-text">${stats.total_all_time}</p>
            </motion.div>

            <motion.div variants={itemVariants} className="bg-white rounded-xl p-6 border border-tally-border">
              <p className="text-sm font-medium text-tally-text/60 mb-2">Expenses</p>
              <p className="text-2xl font-bold text-tally-text">{stats.total_expenses}</p>
            </motion.div>

            <motion.div variants={itemVariants} className="bg-white rounded-xl p-6 border border-tally-border">
              <p className="text-sm font-medium text-tally-text/60 mb-2">Tarjetas</p>
              <p className="text-2xl font-bold text-tally-text">{stats.total_cards}</p>
            </motion.div>

            <motion.div variants={itemVariants} className="bg-white rounded-xl p-6 border border-tally-border">
              <p className="text-sm font-medium text-tally-text/60 mb-2">Pending cuotas</p>
              <p className="text-2xl font-bold text-tally-500">{stats.pending_installments}</p>
            </motion.div>
          </div>
        )}

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Expenses */}
          <motion.div variants={itemVariants} className="lg:col-span-2 bg-white rounded-xl border border-tally-border">
            <div className="px-6 py-4 border-b border-tally-border">
              <h2 className="font-semibold text-tally-text">Recent expenses</h2>
            </div>
            <div className="divide-y divide-tally-border">
              {recentExpenses.length > 0 ? (
                recentExpenses.map((expense) => (
                  <div key={expense.id} className="px-6 py-4 hover:bg-tally-hover transition-colors duration-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-tally-text">{expense.concept}</p>
                        <p className="text-sm text-tally-text/60">
                          {formatDistanceToNow(new Date(expense.date), { addSuffix: true })}
                        </p>
                      </div>
                      <p className="font-semibold text-tally-text">${expense.total_amount}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-6 py-8 text-center text-tally-text/60">
                  No expenses yet
                </div>
              )}
            </div>
          </motion.div>

          {/* Your Debts */}
          <motion.div variants={itemVariants} className="bg-white rounded-xl border border-tally-border">
            <div className="px-6 py-4 border-b border-tally-border">
              <h2 className="font-semibold text-tally-text">You owe</h2>
            </div>
            <div className="divide-y divide-tally-border">
              {debts.length > 0 ? (
                debts.slice(0, 5).map((debt) => (
                  <div key={debt.participant_id} className="px-6 py-4">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-tally-text">{debt.to_user_name}</p>
                      <p className="font-semibold text-tally-text">${debt.amount}</p>
                    </div>
                    <p className="text-xs text-tally-text/60">{debt.concept}</p>
                  </div>
                ))
              ) : (
                <div className="px-6 py-8 text-center text-tally-text/60 text-sm">
                  You are all settled
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </Layout>
  );
}
