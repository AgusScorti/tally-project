// src/pages/SettingsPage.jsx
import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import api from '../api/client';
import { motion } from 'framer-motion';

export default function SettingsPage() {
  const [cards, setCards] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeTab, setActiveTab] = useState('cards');
  const [showCardForm, setShowCardForm] = useState(false);
  const [showCategoryForm, setShowCategoryForm] = useState(false);

  const [cardForm, setCardForm] = useState({
    name: '',
    card_type: 'visa',
    last_four: '',
  });

  const [categoryForm, setCategoryForm] = useState({
    name: '',
    color: '#22C55E',
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [cardsRes, categoriesRes] = await Promise.all([
        api.get('/cards'),
        api.get('/categories'),
      ]);

      setCards(cardsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleAddCard = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/cards', cardForm);
      setCards([...cards, response.data]);
      setShowCardForm(false);
      setCardForm({ name: '', card_type: 'visa', last_four: '' });
    } catch (error) {
      console.error('Error adding card:', error);
    }
  };

  const handleAddCategory = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/categories', categoryForm);
      setCategories([...categories, response.data]);
      setShowCategoryForm(false);
      setCategoryForm({ name: '', color: '#22C55E' });
    } catch (error) {
      console.error('Error adding category:', error);
    }
  };

  const handleDeleteCard = async (cardId) => {
    if (window.confirm('Delete this card?')) {
      try {
        await api.delete(`/cards/${cardId}`);
        setCards(cards.filter((c) => c.id !== cardId));
      } catch (error) {
        console.error('Error deleting card:', error);
      }
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm('Delete this category?')) {
      try {
        await api.delete(`/categories/${categoryId}`);
        setCategories(categories.filter((c) => c.id !== categoryId));
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  return (
    <Layout>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-tally-text mb-2">Settings</h1>
          <p className="text-tally-text/60">Manage your cards and categories</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-tally-border">
          <button
            onClick={() => setActiveTab('cards')}
            className={`px-6 py-4 font-medium border-b-2 transition-colors ${
              activeTab === 'cards'
                ? 'border-tally-500 text-tally-500'
                : 'border-transparent text-tally-text/60'
            }`}
          >
            Cards
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`px-6 py-4 font-medium border-b-2 transition-colors ${
              activeTab === 'categories'
                ? 'border-tally-500 text-tally-500'
                : 'border-transparent text-tally-text/60'
            }`}
          >
            Categories
          </button>
        </div>

        {/* Cards Tab */}
        {activeTab === 'cards' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            <button
              onClick={() => setShowCardForm(!showCardForm)}
              className="bg-tally-500 text-white px-6 py-2.5 rounded-xl font-medium hover:bg-tally-600 transition-colors"
            >
              Add card
            </button>

            {showCardForm && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl border border-tally-border p-6"
              >
                <form onSubmit={handleAddCard} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-label">Card name</label>
                      <input
                        type="text"
                        value={cardForm.name}
                        onChange={(e) => setCardForm({ ...cardForm, name: e.target.value })}
                        className="input-base"
                        placeholder="Visa Personal"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-label">Type</label>
                      <select
                        value={cardForm.card_type}
                        onChange={(e) => setCardForm({ ...cardForm, card_type: e.target.value })}
                        className="input-base"
                      >
                        <option value="visa">Visa</option>
                        <option value="mastercard">Mastercard</option>
                        <option value="amex">American Express</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <label className="text-label">Last 4 digits</label>
                      <input
                        type="text"
                        value={cardForm.last_four}
                        onChange={(e) => setCardForm({ ...cardForm, last_four: e.target.value })}
                        className="input-base"
                        placeholder="4242"
                        maxLength="4"
                      />
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button type="submit" className="btn-primary flex-1">
                      Add card
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCardForm(false)}
                      className="btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </motion.div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cards.map((card) => (
                <motion.div
                  key={card.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-white rounded-xl border border-tally-border p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="font-semibold text-tally-text">{card.name}</p>
                      <p className="text-sm text-tally-text/60">•••• {card.last_four}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteCard(card.id)}
                      className="text-tally-text/40 hover:text-red-500 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                  <p className="text-xs text-tally-text/50 capitalize">{card.card_type}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Categories Tab */}
        {activeTab === 'categories' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            <button
              onClick={() => setShowCategoryForm(!showCategoryForm)}
              className="bg-tally-500 text-white px-6 py-2.5 rounded-xl font-medium hover:bg-tally-600 transition-colors"
            >
              Add category
            </button>

            {showCategoryForm && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl border border-tally-border p-6"
              >
                <form onSubmit={handleAddCategory} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-label">Category name</label>
                      <input
                        type="text"
                        value={categoryForm.name}
                        onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                        className="input-base"
                        placeholder="Entertainment"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-label">Color</label>
                      <div className="flex gap-2">
                        <input
                          type="color"
                          value={categoryForm.color}
                          onChange={(e) => setCategoryForm({ ...categoryForm, color: e.target.value })}
                          className="w-12 h-11 rounded-xl cursor-pointer border border-tally-border"
                        />
                        <input
                          type="text"
                          value={categoryForm.color}
                          onChange={(e) => setCategoryForm({ ...categoryForm, color: e.target.value })}
                          className="flex-1 input-base"
                          placeholder="#22C55E"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button type="submit" className="btn-primary flex-1">
                      Add category
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCategoryForm(false)}
                      className="btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </motion.div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {categories.map((category) => (
                <motion.div
                  key={category.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-white rounded-xl border border-tally-border p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: category.color }}
                      />
                      <p className="font-semibold text-tally-text">{category.name}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteCategory(category.id)}
                      className="text-tally-text/40 hover:text-red-500 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                  <p className="text-xs text-tally-text/50">{category.color}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    </Layout>
  );
}
