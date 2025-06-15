import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  console.log('Middleware executing for path:', request.nextUrl.pathname);
  
  const authToken = request.cookies.get('auth-token');
  const isAuthPage = request.nextUrl.pathname === '/login';
  
  const isAuthenticated = !!authToken;
  console.log('Is authenticated:', isAuthenticated);

  // Redirect to login if not authenticated and trying to access protected routes
  if (!isAuthenticated && !isAuthPage) {
    console.log('Not authenticated, redirecting to login');
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Redirect to dashboard if authenticated and trying to access login page
  if (isAuthenticated && isAuthPage) {
    console.log('Already authenticated, redirecting to dashboard');
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  console.log('Proceeding with request');
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
}; 