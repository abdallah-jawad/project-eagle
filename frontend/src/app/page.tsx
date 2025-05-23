import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to login by default - users must authenticate first
  redirect('/login');
}
