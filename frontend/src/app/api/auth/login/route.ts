import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    console.log('Login attempt:', { email: body.email });
    
    // This is a mock login - replace with your actual authentication logic
    if (body.email === 'test@example.com' && body.password === 'password') {
      const response = {
        user: {
          id: '1',
          email: body.email,
          name: 'Test User',
        },
        token: 'mock-jwt-token',
      };
      console.log('Login successful');
      return NextResponse.json(response);
    }

    console.log('Login failed: Invalid credentials');
    return NextResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 