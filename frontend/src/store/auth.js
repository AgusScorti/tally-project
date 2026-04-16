// src/store/auth.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      
      login: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
      setUser: (user) => set({ user }),
    }),
    {
      name: 'tally-auth',
    }
  )
);

// src/store/expenses.js
import { create } from 'zustand';

export const useExpensesStore = create((set, get) => ({
  expenses: [],
  loading: false,
  error: null,
  
  setExpenses: (expenses) => set({ expenses }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  addExpense: (expense) => {
    const current = get().expenses;
    set({ expenses: [expense, ...current] });
  },
}));

// src/store/payments.js
import { create } from 'zustand';

export const usePaymentsStore = create((set, get) => ({
  debts: [],
  credits: [],
  balances: {},
  loading: false,
  
  setDebts: (debts) => set({ debts }),
  setCredits: (credits) => set({ credits }),
  setBalances: (balances) => set({ balances }),
  setLoading: (loading) => set({ loading }),
}));
