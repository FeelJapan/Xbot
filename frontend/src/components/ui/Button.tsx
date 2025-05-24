import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  className = '',
  disabled = false
}) => {
  const baseStyles = `
    rounded-lg
    font-medium
    transition-all
    duration-300
    transform
    hover:scale-105
    active:scale-95
    disabled:opacity-50
    disabled:cursor-not-allowed
    disabled:hover:scale-100
  `;

  const variantStyles = {
    primary: `
      bg-primary-500
      hover:bg-primary-600
      text-white
      shadow-lg
      hover:shadow-xl
    `,
    secondary: `
      bg-gray-200
      hover:bg-gray-300
      text-gray-800
      dark:bg-gray-700
      dark:hover:bg-gray-600
      dark:text-white
    `,
    outline: `
      border-2
      border-primary-500
      text-primary-500
      hover:bg-primary-50
      dark:hover:bg-primary-900/20
    `
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseStyles}
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `}
    >
      {children}
    </button>
  );
}; 