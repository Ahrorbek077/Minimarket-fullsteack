import { create } from "zustand";
import type { Cart, CartItem } from "@/types";

interface CartState {
  cart:       Cart;
  isLoading:  boolean;
  setCart:    (cart: Cart) => void;
  setLoading: (v: boolean) => void;
  clearCart:  () => void;
}

const EMPTY_CART: Cart = { items: [], item_count: 0, total_amount: "0.00" };

export const useCartStore = create<CartState>((set) => ({
  cart:       EMPTY_CART,
  isLoading:  false,
  setCart:    (cart) => set({ cart }),
  setLoading: (isLoading) => set({ isLoading }),
  clearCart:  () => set({ cart: EMPTY_CART }),
}));
