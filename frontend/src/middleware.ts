import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Himoyalangan sahifalar — login talab qilinadi
const PROTECTED = [
  "/", "/pos", "/products", "/purchases", "/companies",
  "/inventory", "/sales", "/history", "/reports", "/settings"
];

// Autentifikatsiya sahifalari
const AUTH_PAGES = ["/login"];

// ✅ To'g'ri nom: 'middleware' (proxy emas!)
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const accessToken = request.cookies.get("access_token_present")?.value;

  const isProtected = PROTECTED.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );
  const isAuthPage = AUTH_PAGES.some((p) => pathname.startsWith(p));

  if (isProtected && !accessToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("from", pathname);
    return NextResponse.redirect(url);
  }

  if (isAuthPage && accessToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.png).*)"],
};
