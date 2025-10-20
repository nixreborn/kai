/**
 * JournalEditor component - Rich text editor for journal entries
 */

'use client';

import { useState, useEffect } from 'react';
import { Smile, Image as ImageIcon } from 'lucide-react';

interface JournalEditorProps {
  title?: string;
  content?: string;
  mood?: number | null;
  moodEmoji?: string | null;
  onTitleChange?: (title: string) => void;
  onContentChange?: (content: string) => void;
  onMoodChange?: (mood: number | null, emoji: string | null) => void;
  placeholder?: string;
  disabled?: boolean;
}

const MOOD_OPTIONS = [
  { value: 1, emoji: '😭', label: 'Terrible' },
  { value: 2, emoji: '😢', label: 'Very Bad' },
  { value: 3, emoji: '😟', label: 'Bad' },
  { value: 4, emoji: '😕', label: 'Not Great' },
  { value: 5, emoji: '😐', label: 'Okay' },
  { value: 6, emoji: '🙂', label: 'Good' },
  { value: 7, emoji: '😊', label: 'Pretty Good' },
  { value: 8, emoji: '😄', label: 'Great' },
  { value: 9, emoji: '😁', label: 'Wonderful' },
  { value: 10, emoji: '🤩', label: 'Amazing' },
];

export function JournalEditor({
  title = '',
  content = '',
  mood = null,
  moodEmoji = null,
  onTitleChange,
  onContentChange,
  onMoodChange,
  placeholder = 'What\'s on your mind?',
  disabled = false,
}: JournalEditorProps) {
  const [localTitle, setLocalTitle] = useState(title);
  const [localContent, setLocalContent] = useState(content);
  const [showMoodPicker, setShowMoodPicker] = useState(false);
  const [charCount, setCharCount] = useState(content.length);

  useEffect(() => {
    setLocalTitle(title);
  }, [title]);

  useEffect(() => {
    setLocalContent(content);
    setCharCount(content.length);
  }, [content]);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = e.target.value;
    setLocalTitle(newTitle);
    onTitleChange?.(newTitle);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setLocalContent(newContent);
    setCharCount(newContent.length);
    onContentChange?.(newContent);
  };

  const handleMoodSelect = (value: number, emoji: string) => {
    onMoodChange?.(value, emoji);
    setShowMoodPicker(false);
  };

  const selectedMood = mood ? MOOD_OPTIONS.find(m => m.value === mood) : null;

  return (
    <div className="space-y-4">
      {/* Title Input */}
      <div>
        <input
          type="text"
          value={localTitle}
          onChange={handleTitleChange}
          placeholder="Entry title (optional)"
          disabled={disabled}
          className="w-full px-4 py-3 text-2xl font-semibold bg-transparent border-0 border-b-2 border-gray-200 dark:border-gray-700 focus:border-aqua-500 dark:focus:border-aqua-400 focus:outline-none transition-colors placeholder:text-gray-400 dark:placeholder:text-gray-600 text-gray-800 dark:text-gray-200"
        />
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-2 px-2">
        {/* Mood Picker */}
        <div className="relative">
          <button
            onClick={() => setShowMoodPicker(!showMoodPicker)}
            disabled={disabled}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Select mood"
          >
            {selectedMood ? (
              <>
                <span className="text-2xl">{selectedMood.emoji}</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {selectedMood.label}
                </span>
              </>
            ) : (
              <>
                <Smile className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  How are you feeling?
                </span>
              </>
            )}
          </button>

          {/* Mood Picker Dropdown */}
          {showMoodPicker && (
            <div className="absolute top-full left-0 mt-2 w-80 p-4 bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-10 animate-slide-up">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                How are you feeling?
              </h3>
              <div className="grid grid-cols-5 gap-2">
                {MOOD_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleMoodSelect(option.value, option.emoji)}
                    className={`flex flex-col items-center p-2 rounded-lg hover:bg-aqua-50 dark:hover:bg-aqua-950/20 transition-colors ${
                      mood === option.value
                        ? 'bg-aqua-100 dark:bg-aqua-900/30 ring-2 ring-aqua-500'
                        : ''
                    }`}
                    title={option.label}
                  >
                    <span className="text-2xl mb-1">{option.emoji}</span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {option.value}
                    </span>
                  </button>
                ))}
              </div>
              <button
                onClick={() => {
                  onMoodChange?.(null, null);
                  setShowMoodPicker(false);
                }}
                className="w-full mt-3 px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                Clear mood
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content Textarea */}
      <div className="relative">
        <textarea
          value={localContent}
          onChange={handleContentChange}
          placeholder={placeholder}
          disabled={disabled}
          rows={12}
          className="w-full px-4 py-3 bg-transparent border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-aqua-500 dark:focus:border-aqua-400 focus:outline-none transition-colors resize-none placeholder:text-gray-400 dark:placeholder:text-gray-600 text-gray-800 dark:text-gray-200"
        />

        {/* Character count */}
        <div className="absolute bottom-3 right-3 text-xs text-gray-400 dark:text-gray-600">
          {charCount} characters
        </div>
      </div>

      {/* Writing tips */}
      {charCount === 0 && (
        <div className="p-4 bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 border border-aqua-200 dark:border-aqua-800 rounded-xl">
          <h4 className="text-sm font-semibold text-aqua-800 dark:text-aqua-300 mb-2">
            Writing tips
          </h4>
          <ul className="text-xs text-aqua-700 dark:text-aqua-400 space-y-1">
            <li>• Write freely without judgment</li>
            <li>• Focus on your feelings and experiences</li>
            <li>• There's no right or wrong way to journal</li>
            <li>• Be honest with yourself</li>
          </ul>
        </div>
      )}
    </div>
  );
}
