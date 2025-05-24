import React from 'react';

interface InputProps {
  label: string;
  type?: string;
  error?: string;
  value: string;
  onChange: (value: string) => void;
  className?: string;
  placeholder?: string;
  required?: boolean;
}

export const Input: React.FC<InputProps> = ({
  label,
  type = 'text',
  error,
  value,
  onChange,
  className = '',
  placeholder = '',
  required = false
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      <label className="
        block
        text-sm
        font-medium
        text-gray-700
        dark:text-gray-300
      ">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className={`
          w-full
          px-4
          py-2
          rounded-lg
          border
          transition-all
          duration-200
          focus:ring-2
          focus:ring-primary-500
          focus:border-transparent
          ${
            error
              ? 'border-red-500'
              : 'border-gray-300 dark:border-gray-600'
          }
          bg-white
          dark:bg-gray-700
          text-gray-900
          dark:text-white
          placeholder-gray-400
          dark:placeholder-gray-500
        `}
      />
      
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}; 