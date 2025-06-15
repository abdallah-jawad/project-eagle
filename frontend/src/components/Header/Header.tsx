'use client';

import { FC, useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import styles from './Header.module.css';
import { HeaderProps } from './types';
import LogoutButton from '../auth/LogoutButton';

const Header: FC<HeaderProps> = ({ title = 'Project Eagle', user }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <h1>{title}</h1>
      </div>
      <div className={styles.userSection} ref={dropdownRef}>
        <button 
          className={styles.userBadge}
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        >
          {user.avatar ? (
            <Image
              src={user.avatar}
              alt={user.name}
              width={32}
              height={32}
              className={styles.avatar}
            />
          ) : (
            user.name.charAt(0).toUpperCase()
          )}
        </button>
        
        {isDropdownOpen && (
          <div className={styles.dropdown}>
            <div className={styles.dropdownHeader}>
              <span className={styles.userName}>{user.name}</span>
            </div>
            <div className={styles.dropdownContent}>
              <LogoutButton />
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header; 