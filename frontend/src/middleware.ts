import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  console.log('Middleware executing for path:', request.nextUrl.pathname);

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-url', request.url);
  
  const token = request.cookies.get('auth-storage');
  const isAuthPage = request.nextUrl.pathname === '/login';
  
  console.log('Auth state:', { 
    hasToken: !!token, 
    isAuthPage,
    path: request.nextUrl.pathname 
  });

  // During development, allow access to dashboard
  if (process.env.NODE_ENV === 'development') {
    console.log('Development mode: allowing access');
    return NextResponse.next();
  }

  if (!token && !isAuthPage) {
    console.log('No token, redirecting to login');
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (token && isAuthPage) {
    console.log('Has token, redirecting to dashboard');
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  console.log('Proceeding with request');
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
}; 