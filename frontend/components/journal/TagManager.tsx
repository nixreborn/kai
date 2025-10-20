/**
 * TagManager component - Add, remove, and manage tags for journal entries
 */

'use client';

import { useState } from 'react';
import { X, Plus, Tag } from 'lucide-react';

interface TagManagerProps {
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  suggestions?: string[];
  maxTags?: number;
  disabled?: boolean;
}

const DEFAULT_SUGGESTIONS = [
  'gratitude',
  'reflection',
  'anxiety',
  'happiness',
  'growth',
  'challenges',
  'relationships',
  'work',
  'health',
  'mindfulness',
  'goals',
  'emotions',
];

export function TagManager({
  tags,
  onTagsChange,
  suggestions = DEFAULT_SUGGESTIONS,
  maxTags = 10,
  disabled = false,
}: TagManagerProps) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleAddTag = (tag: string) => {
    const normalizedTag = tag.trim().toLowerCase();

    if (!normalizedTag) return;
    if (tags.includes(normalizedTag)) return;
    if (tags.length >= maxTags) return;

    onTagsChange([...tags, normalizedTag]);
    setInputValue('');
    setShowSuggestions(false);
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onTagsChange(tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag(inputValue);
    } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
      // Remove last tag on backspace when input is empty
      handleRemoveTag(tags[tags.length - 1]);
    }
  };

  const filteredSuggestions = suggestions.filter(
    (suggestion) =>
      !tags.includes(suggestion) &&
      suggestion.toLowerCase().includes(inputValue.toLowerCase())
  );

  return (
    <div className="space-y-3">
      {/* Tags Display */}
      <div className="flex flex-wrap gap-2 min-h-[32px]">
        {tags.map((tag) => (
          <div
            key={tag}
            className="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-br from-aqua-100 to-ocean-100 dark:from-aqua-900/30 dark:to-ocean-900/30 text-aqua-700 dark:text-aqua-300 text-sm rounded-full border border-aqua-300 dark:border-aqua-700 animate-fade-in"
          >
            <Tag className="w-3 h-3" />
            <span>{tag}</span>
            {!disabled && (
              <button
                onClick={() => handleRemoveTag(tag)}
                className="ml-1 hover:text-aqua-900 dark:hover:text-aqua-100 transition-colors"
                aria-label={`Remove ${tag} tag`}
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ))}

        {/* Input */}
        {!disabled && tags.length < maxTags && (
          <div className="relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                setShowSuggestions(e.target.value.length > 0);
              }}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowSuggestions(inputValue.length > 0)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              placeholder={tags.length === 0 ? 'Add tags...' : ''}
              className="px-3 py-1 min-w-[120px] bg-transparent border border-dashed border-gray-300 dark:border-gray-600 rounded-full text-sm focus:outline-none focus:border-aqua-500 dark:focus:border-aqua-400 transition-colors placeholder:text-gray-400 dark:placeholder:text-gray-600"
            />

            {/* Suggestions Dropdown */}
            {showSuggestions && filteredSuggestions.length > 0 && (
              <div className="absolute top-full left-0 mt-2 w-64 max-h-48 overflow-y-auto bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-10 animate-slide-up">
                <div className="p-2">
                  <p className="px-2 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400">
                    Suggestions
                  </p>
                  {filteredSuggestions.slice(0, 8).map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleAddTag(suggestion)}
                      className="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-aqua-50 dark:hover:bg-aqua-950/20 rounded-lg transition-colors flex items-center gap-2"
                    >
                      <Tag className="w-3 h-3 text-aqua-500" />
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Tag count indicator */}
      {!disabled && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {tags.length}/{maxTags} tags
          {tags.length === maxTags && ' (maximum reached)'}
        </div>
      )}

      {/* Quick add suggestions (when no tags) */}
      {!disabled && tags.length === 0 && !showSuggestions && (
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 dark:text-gray-400 self-center">
            Quick add:
          </span>
          {DEFAULT_SUGGESTIONS.slice(0, 5).map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => handleAddTag(suggestion)}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs text-gray-600 dark:text-gray-400 hover:text-aqua-700 dark:hover:text-aqua-300 hover:bg-aqua-50 dark:hover:bg-aqua-950/20 rounded-full transition-colors border border-transparent hover:border-aqua-300 dark:hover:border-aqua-700"
            >
              <Plus className="w-3 h-3" />
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
