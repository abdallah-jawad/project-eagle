import { ReactNode } from 'react';

export interface LayoutProps {
  children: ReactNode;
  user?: {
    name: string;
    avatar?: string;
  };
} 