// src/pages/PaymentsPage.jsx
import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import api from '../api/client';
import { motion } from 'framer-motion';

export default function PaymentsPage() {
  const [debts, setDebts] = useState([]);
  const [credits, setCredits] = useState([]);
  const [activeTab, setActiveTab] = useState('owe');
  const [loading, setLoading] = useState(true);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [paymentData, setPaymentData] = useState({
    to_user_id: '',
    amount: '',
    description: '',
  });

  useEffect(() => {
    fetchPaymentData();
  }, []);

  const fetchPaymentData = async () => {
    try {
      const [debtsRes, creditsRes] = await Promise.all([
        api.get('/payments/me/owe'),
        api.get('/payments/me/owed'),
      ]);

      setDebts(debtsRes.data);
      setCredits(creditsRes.data);
    } catch (error) {
      console.error('Error fetching payments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (e) => {
    e.preventDefault();
    try {
      await api.post('/payments', {
        ...paymentData,
        amount: parseFloat(paymentData.amount),
      });

      setShowPaymentForm(false);
      setPaymentData({ to_user_id: '', amount: '', description: '' });
      fetchPaymentData();
    } catch (error) {
      console.error('Error creating payment:', error);
    }
  };

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-8"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-tally-text mb-2">Payments</h1>
            <p className="text-tally-text/60">Manage who owes whom</p>
          </div>
          <button
            onClick={() => setShowPaymentForm(!showPaymentForm)}
            className="bg-tally-500 text-white px-6 py-2.5 rounded-xl font-medium hover:bg-tally-600 transition-colors duration-200"
          >
            Record payment
          </button>
        </div>

        {/* Payment Form */}
        {showPaymentForm && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl border border-tally-border p-6"
          >
            <form onSubmit={handlePayment} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-label">Pay to</label>
                  <input
                    type="number"
                    value={paymentData.to_user_id}
                    onChange={(e) => setPaymentData({ ...paymentData, to_user_id: e.target.value })}
                    className="input-base"
                    placeholder="User ID"
                    required
                  />
                </div>

                <div>
                  <label className="text-label">Amount</label>
                  <input
                    type="number"
                    value={paymentData.amount}
                    onChange={(e) => setPaymentData({ ...paymentData, amount: e.target.value })}
                    className="input-base"
                    placeholder="100.00"
                    step="0.01"
                    required
                  />
                </div>

                <div>
                  <label className="text-label">Note</label>
                  <input
                    type="text"
                    value={paymentData.description}
                    onChange={(e) => setPaymentData({ ...paymentData, description: e.target.value })}
                    className="input-base"
                    placeholder="Payment for..."
                  />
                </div>
              </div>

              <div className="flex gap-3">
                <button type="submit" className="btn-primary flex-1">
                  Send payment
                </button>
                <button
                  type="button"
                  onClick={() => setShowPaymentForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 border-b border-tally-border">
          <button
            onClick={() => setActiveTab('owe')}
            className={`px-6 py-4 font-medium border-b-2 transition-colors ${
              activeTab === 'owe'
                ? 'border-tally-500 text-tally-500'
                : 'border-transparent text-tally-text/60 hover:text-tally-text'
            }`}
          >
            You owe ({debts.length})
          </button>
          <button
            onClick={() => setActiveTab('owed')}
            className={`px-6 py-4 font-medium border-b-2 transition-colors ${
              activeTab === 'owed'
                ? 'border-tally-500 text-tally-500'
                : 'border-transparent text-tally-text/60 hover:text-tally-text'
            }`}
          >
            Owed to you ({credits.length})
          </button>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {activeTab === 'owe' && (
            <div className="lg:col-span-2 bg-white rounded-xl border border-tally-border">
              <div className="px-6 py-4 border-b border-tally-border">
                <h2 className="font-semibold text-tally-text">What you owe</h2>
              </div>
              <div className="divide-y divide-tally-border">
                {debts.length > 0 ? (
                  debts.map((debt) => (
                    <motion.div
                      key={debt.participant_id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="px-6 py-4 hover:bg-tally-hover transition-colors duration-200"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-tally-text">{debt.to_user_name}</p>
                          <p className="text-sm text-tally-text/60">{debt.concept}</p>
                        </div>
                        <p className="font-semibold text-tally-500">${debt.amount}</p>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="px-6 py-12 text-center text-tally-text/60">
                    You are all settled
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'owed' && (
            <div className="lg:col-span-2 bg-white rounded-xl border border-tally-border">
              <div className="px-6 py-4 border-b border-tally-border">
                <h2 className="font-semibold text-tally-text">What you are owed</h2>
              </div>
              <div className="divide-y divide-tally-border">
                {credits.length > 0 ? (
                  credits.map((credit) => (
                    <motion.div
                      key={credit.participant_id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="px-6 py-4 hover:bg-tally-hover transition-colors duration-200"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-tally-text">{credit.from_user_name}</p>
                          <p className="text-sm text-tally-text/60">{credit.concept}</p>
                        </div>
                        <p className="font-semibold text-tally-500">${credit.amount}</p>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="px-6 py-12 text-center text-tally-text/60">
                    Nobody owes you anything
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </Layout>
  );
}
