'use client';

import { FC, useState } from 'react';
import { usePathname } from 'next/navigation';
import {
  HomeIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import Header from '../Header/Header';
import Sidebar from '../Sidebar/Sidebar';
import styles from './MainLayout.module.css';
import { useAuthStore } from '@/store/auth';
import { LayoutProps } from './types';

const MainLayout: FC<LayoutProps> = ({ children }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const pathname = usePathname();
  const isLoginPage = pathname === '/login/' || pathname === '/login';
  const user = useAuthStore((state) => state.user);

  // Transform user data to match Header's expected format
  const headerUser = user ? {
    name: user.name,
    avatar: undefined
  } : undefined;

  const navItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: <HomeIcon className="w-6 h-6" />,
    },
    {
      label: 'Analytics',
      path: '/analytics',
      icon: <ChartBarIcon className="w-6 h-6" />,
    },
    {
      label: 'Settings',
      path: '/settings',
      icon: <Cog6ToothIcon className="w-6 h-6" />,
    },
  ];

  // If we're on the login page, just render the children without the layout
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Otherwise render the full layout
  return (
    <div className={styles.layout}>
      <Sidebar
        navItems={navItems}
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className={`${styles.main} ${isSidebarCollapsed ? styles.mainExpanded : ''}`}>
        <Header user={headerUser} />
        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
};

export default MainLayout; 