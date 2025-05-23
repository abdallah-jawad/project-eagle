'use client';

import { FC } from 'react';
import Image from 'next/image';
import styles from './Header.module.css';
import { HeaderProps } from './types';

const Header: FC<HeaderProps> = ({ title = 'Project Eagle', user }) => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <h1>{title}</h1>
      </div>
      <div className={styles.userSection}>
        {user && (
          <div className={styles.userInfo}>
            {user.avatar && (
              <Image
                src={user.avatar}
                alt={user.name}
                width={32}
                height={32}
                className={styles.avatar}
              />
            )}
            <span className={styles.userName}>{user.name}</span>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header; 