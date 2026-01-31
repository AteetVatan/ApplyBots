"use client";

import { Search, X } from "lucide-react";
import { useState, useEffect, useRef } from "react";

interface SearchFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export function SearchFilter({ value, onChange }: SearchFilterProps) {
  const [localValue, setLocalValue] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce the onChange callback with proper cleanup
  useEffect(() => {
    // Clear any existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    // Only debounce if localValue differs from the prop value
    if (localValue !== value) {
      timerRef.current = setTimeout(() => {
        onChange(localValue);
      }, 300);
    }

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [localValue, onChange, value]);

  const handleClear = () => {
    setLocalValue("");
    onChange("");
  };

  return (
    <div className="relative">
      <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500" />
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder="Search by job title or company..."
        className="w-full pl-12 pr-10 py-3 bg-neutral-900/50 border border-neutral-800 rounded-xl text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/25 transition-colors"
      />
      {localValue && (
        <button
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-lg hover:bg-neutral-800 transition-colors"
          aria-label="Clear search"
        >
          <X className="w-4 h-4 text-neutral-500" />
        </button>
      )}
    </div>
  );
}
