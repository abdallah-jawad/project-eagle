import { ReactNode } from 'react';

export interface NavItem {
  label: string;
  path: string;
  icon?: ReactNode;
}

export interface SidebarProps {
  navItems: NavItem[];
  isCollapsed?: boolean;
  onToggle?: () => void;
} 