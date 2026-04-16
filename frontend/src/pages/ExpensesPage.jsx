// src/pages/ExpensesPage.jsx
import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../api/client';
import { motion } from 'framer-motion';

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [cards, setCards] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState({
    card_id: '',
    category_id: '',
    concept: '',
    total_amount: '',
    date: new Date().toISOString().split('T')[0],
    has_installments: false,
    num_installments: 1,
    participants: [{ user_id: 1, amount: '' }],
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [expensesRes, cardsRes, categoriesRes] = await Promise.all([
        api.get('/expenses'),
        api.get('/cards'),
        api.get('/categories'),
      ]);

      setExpenses(expensesRes.data);
      setCards(cardsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/expenses', {
        ...formData,
        total_amount: parseFloat(formData.total_amount),
        card_id: parseInt(formData.card_id),
        category_id: parseInt(formData.category_id),
      });

      setExpenses([response.data, ...expenses]);
      setShowForm(false);
      setFormData({
        card_id: '',
        category_id: '',
        concept: '',
        total_amount: '',
        date: new Date().toISOString().split('T')[0],
        has_installments: false,
        num_installments: 1,
        participants: [{ user_id: 1, amount: '' }],
      });
    } catch (error) {
      console.error('Error creating expense:', error);
    }
  };

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-8"
      >
        {/* Header with Button */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-tally-text mb-2">Expenses</h1>
            <p className="text-tally-text/60">Track all your spending</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-tally-500 text-white px-6 py-2.5 rounded-xl font-medium hover:bg-tally-600 transition-colors duration-200"
          >
            New expense
          </button>
        </div>

        {/* New Expense Form */}
        {showForm && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl border border-tally-border p-6"
          >
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Concept
                  </label>
                  <input
                    type="text"
                    value={formData.concept}
                    onChange={(e) => setFormData({ ...formData, concept: e.target.value })}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all"
                    placeholder="Dinner"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Amount
                  </label>
                  <input
                    type="number"
                    value={formData.total_amount}
                    onChange={(e) => setFormData({ ...formData, total_amount: e.target.value })}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all"
                    placeholder="100"
                    step="0.01"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Card
                  </label>
                  <select
                    value={formData.card_id}
                    onChange={(e) => setFormData({ ...formData, card_id: e.target.value })}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all"
                    required
                  >
                    <option value="">Select a card</option>
                    {cards.map((card) => (
                      <option key={card.id} value={card.id}>
                        {card.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Category
                  </label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all"
                    required
                  >
                    <option value="">Select a category</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Date
                  </label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Installments
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="checkbox"
                      checked={formData.has_installments}
                      onChange={(e) => setFormData({ ...formData, has_installments: e.target.checked })}
                      className="w-5 h-5 rounded border-tally-border accent-tally-500"
                    />
                    {formData.has_installments && (
                      <input
                        type="number"
                        value={formData.num_installments}
                        onChange={(e) => setFormData({ ...formData, num_installments: parseInt(e.target.value) })}
                        min="2"
                        max="60"
                        className="flex-1 px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all"
                        placeholder="Number of installments"
                      />
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-tally-500 text-white py-2.5 rounded-xl font-medium hover:bg-tally-600 transition-colors"
                >
                  Create expense
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 bg-tally-border text-tally-text py-2.5 rounded-xl font-medium hover:bg-tally-hover transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {/* Expenses List */}
        <div className="bg-white rounded-xl border border-tally-border overflow-hidden">
          <div className="px-6 py-4 border-b border-tally-border">
            <h2 className="font-semibold text-tally-text">All expenses</h2>
          </div>
          <div className="divide-y divide-tally-border">
            {expenses.length > 0 ? (
              expenses.map((expense) => (
                <motion.div
                  key={expense.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="px-6 py-4 hover:bg-tally-hover transition-colors duration-200"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-tally-text">{expense.concept}</p>
                      <p className="text-sm text-tally-text/60">{new Date(expense.date).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-tally-text">${expense.total_amount}</p>
                      {expense.has_installments && (
                        <p className="text-xs text-tally-text/60">{expense.num_installments} installments</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="px-6 py-12 text-center text-tally-text/60">
                No expenses yet. Create one to get started.
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </Layout>
  );
}
