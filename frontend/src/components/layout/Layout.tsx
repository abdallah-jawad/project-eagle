'use client';

import { FC, useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import {
  HomeIcon,
  UserGroupIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import Header from '../Header/Header';
import Sidebar from '../Sidebar/Sidebar';
import styles from './Layout.module.css';
import { LayoutProps } from './types';

const Layout: FC<LayoutProps> = ({ children, user }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showLayout, setShowLayout] = useState(true);
  const pathname = usePathname();

  useEffect(() => {
    setShowLayout(pathname !== '/login');
  }, [pathname]);

  if (!showLayout) {
    return <>{children}</>;
  }

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

  return (
    <div className={styles.layout}>
      <Sidebar
        navItems={navItems}
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className={`${styles.main} ${isSidebarCollapsed ? styles.mainExpanded : ''}`}>
        <Header user={user} />
        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
};

export default Layout; 