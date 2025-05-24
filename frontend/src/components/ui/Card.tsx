import React from 'react';

interface CardProps {
  title: string;
  children: React.ReactNode;
  image?: string;
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  children,
  image,
  className = ''
}) => {
  return (
    <div className={`
      bg-white
      dark:bg-gray-800
      rounded-xl
      shadow-lg
      hover:shadow-xl
      transition-all
      duration-300
      overflow-hidden
      hover:-translate-y-1
      ${className}
    `}>
      {image && (
        <div className="relative h-48 overflow-hidden">
          <img
            src={image}
            alt={title}
            className="
              w-full
              h-full
              object-cover
              transform
              hover:scale-110
              transition-transform
              duration-300
            "
          />
        </div>
      )}
      
      <div className="p-6">
        <h3 className="
          text-xl
          font-bold
          text-gray-800
          dark:text-white
          mb-4
        ">
          {title}
        </h3>
        
        <div className="
          text-gray-600
          dark:text-gray-300
        ">
          {children}
        </div>
      </div>
    </div>
  );
}; 