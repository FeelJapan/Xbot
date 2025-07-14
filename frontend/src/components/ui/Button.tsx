import React from 'react';
import { Button as HeroButton } from "@heroui/react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'solid' | 'bordered' | 'light' | 'flat' | 'faded' | 'shadow' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'solid',
  size = 'md',
  className = '',
}) => {
  return (
    <HeroButton
      className={`relative overflow-visible rounded-full hover:-translate-y-1 transition-transform ${className}`}
      size={size}
      variant={variant}
      onPress={onClick}
    >
      {children}
    </HeroButton>
  );
}; 