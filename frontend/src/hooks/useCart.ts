import { useCallback } from "react";
import { toast } from "react-hot-toast";
import { useCartStore } from "@/store/cartStore";
import { cartService } from "@/services/cart.service";

export function useCart() {
  const { cart, isLoading, setCart, setLoading } = useCartStore();

  const fetchCart = useCallback(async () => {
    setLoading(true);
    try {
      const data = await cartService.getCart();
      setCart(data);
    } finally {
      setLoading(false);
    }
  }, [setCart, setLoading]);

  const scan = useCallback(async (barcode: string) => {
    setLoading(true);
    try {
      const data = await cartService.scan(barcode);
      setCart(data);
      toast.success("Mahsulot qo'shildi");
    } catch {
      toast.error("Mahsulot topilmadi");
    } finally {
      setLoading(false);
    }
  }, [setCart, setLoading]);

  const addItem = useCallback(async (product_id: number, quantity = 1) => {
    setLoading(true);
    try {
      const data = await cartService.addItem(product_id, quantity);
      setCart(data);
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato yuz berdi");
    } finally {
      setLoading(false);
    }
  }, [setCart, setLoading]);

  const updateItem = useCallback(async (product_id: number, quantity: number) => {
    setLoading(true);
    try {
      const data = await cartService.updateItem(product_id, quantity);
      setCart(data);
    } finally {
      setLoading(false);
    }
  }, [setCart, setLoading]);

  const removeItem = useCallback(async (product_id: number) => {
    setLoading(true);
    try {
      const data = await cartService.removeItem(product_id);
      setCart(data);
    } finally {
      setLoading(false);
    }
  }, [setCart, setLoading]);

  const clear = useCallback(async () => {
    await cartService.clear();
    useCartStore.getState().clearCart();
  }, []);

  return { cart, isLoading, fetchCart, scan, addItem, updateItem, removeItem, clear };
}
