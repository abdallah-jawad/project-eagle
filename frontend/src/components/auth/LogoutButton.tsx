'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

export default function LogoutButton() {
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <button
      onClick={handleLogout}
      className="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors cursor-pointer text-left flex items-center gap-2 group"
    >
      <ArrowRightOnRectangleIcon className="w-5 h-5 text-gray-500 group-hover:text-gray-700" />
      <span>Sign Out</span>
    </button>
  );
} 