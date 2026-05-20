import { useAuthStore } from "@/store/authStore";
import type { UserRole } from "@/types";

export function useAuth() {
  const { user, isAuth, logout } = useAuthStore();

  const hasRole = (...roles: UserRole[]) =>
    !!user && roles.includes(user.role);

  const isAdmin      = hasRole("super_admin", "admin");
  const isCashier    = hasRole("super_admin", "admin", "cashier");
  const isStorekeeper= hasRole("super_admin", "admin", "storekeeper");
  const isAccountant = hasRole("super_admin", "admin", "accountant");

  return { user, isAuth, logout, hasRole, isAdmin, isCashier, isStorekeeper, isAccountant };
}
