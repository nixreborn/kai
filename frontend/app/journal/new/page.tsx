/**
 * New Journal Entry page - Create a new journal entry
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useJournal } from '@/hooks/useJournal';
import { JournalEditor } from '@/components/journal/JournalEditor';
import { TagManager } from '@/components/journal/TagManager';
import { Save, X, Sparkles, ArrowLeft } from 'lucide-react';
import { JournalPrompt } from '@/lib/types/journal';

// Get user ID from localStorage
const getUserId = () => {
  if (typeof window === 'undefined') return 'demo-user';
  let userId = localStorage.getItem('kai-user-id');
  if (!userId) {
    userId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('kai-user-id', userId);
  }
  return userId;
};

export default function NewJournalEntryPage() {
  const router = useRouter();
  const [userId] = useState(getUserId);
  const { createEntry, getPrompts, isLoading, error } = useJournal({ userId, autoLoad: false });

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [mood, setMood] = useState<number | null>(null);
  const [moodEmoji, setMoodEmoji] = useState<string | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [showPrompts, setShowPrompts] = useState(false);
  const [prompts, setPrompts] = useState<JournalPrompt[]>([]);
  const [loadingPrompts, setLoadingPrompts] = useState(false);

  const handleMoodChange = (newMood: number | null, emoji: string | null) => {
    setMood(newMood);
    setMoodEmoji(emoji);
  };

  const handleSave = async () => {
    if (!content.trim()) {
      alert('Please write something before saving.');
      return;
    }

    setIsSaving(true);
    try {
      const entry = await createEntry({
        title: title.trim() || null,
        content: content.trim(),
        mood,
        mood_emoji: moodEmoji,
        tags,
      });

      if (entry) {
        // Navigate to the created entry
        router.push(`/journal/${entry.id}`);
      }
    } catch (err) {
      console.error('Error saving entry:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (content.trim() || title.trim()) {
      if (!confirm('You have unsaved changes. Are you sure you want to leave?')) {
        return;
      }
    }
    router.push('/journal');
  };

  const handleGetPrompts = async () => {
    setLoadingPrompts(true);
    setShowPrompts(true);
    try {
      const response = await getPrompts();
      if (response) {
        setPrompts(response.prompts);
      }
    } catch (err) {
      console.error('Error getting prompts:', err);
    } finally {
      setLoadingPrompts(false);
    }
  };

  const handleUsePrompt = (prompt: string) => {
    setContent((prev) => (prev ? `${prev}\n\n${prompt}` : prompt));
    setShowPrompts(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={handleCancel}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                aria-label="Go back"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  New Journal Entry
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date().toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCancel}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>

              <button
                onClick={handleSave}
                disabled={isSaving || !content.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-aqua-500 to-ocean-500 text-white rounded-lg hover:from-aqua-600 hover:to-ocean-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
              >
                <Save className="w-4 h-4" />
                {isSaving ? 'Saving...' : 'Save Entry'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div className="max-w-4xl mx-auto px-4 pt-4">
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Prompts Section */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <button
            onClick={handleGetPrompts}
            disabled={loadingPrompts}
            className="flex items-center gap-2 text-sm text-aqua-600 dark:text-aqua-400 hover:text-aqua-700 dark:hover:text-aqua-300 transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {loadingPrompts ? 'Loading prompts...' : 'Get writing prompts from Kai'}
          </button>

          {showPrompts && prompts.length > 0 && (
            <div className="mt-4 space-y-2 animate-slide-up">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Writing prompts for you:
              </h3>
              {prompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleUsePrompt(prompt.prompt)}
                  className="w-full text-left p-3 bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 border border-aqua-200 dark:border-aqua-800 rounded-lg hover:border-aqua-400 dark:hover:border-aqua-600 transition-all group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-gray-700 dark:text-gray-300 flex-1">
                      {prompt.prompt}
                    </p>
                    <span className="px-2 py-0.5 bg-aqua-100 dark:bg-aqua-900/30 text-aqua-700 dark:text-aqua-300 text-xs rounded-full capitalize flex-shrink-0">
                      {prompt.category}
                    </span>
                  </div>
                  <p className="text-xs text-aqua-600 dark:text-aqua-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    Click to use this prompt
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Editor */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <JournalEditor
            title={title}
            content={content}
            mood={mood}
            moodEmoji={moodEmoji}
            onTitleChange={setTitle}
            onContentChange={setContent}
            onMoodChange={handleMoodChange}
            disabled={isSaving}
          />
        </div>

        {/* Tags */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Tags
          </h3>
          <TagManager tags={tags} onTagsChange={setTags} disabled={isSaving} />
        </div>

        {/* Tips */}
        <div className="p-4 bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 border border-aqua-200 dark:border-aqua-800 rounded-xl">
          <h4 className="text-sm font-semibold text-aqua-800 dark:text-aqua-300 mb-2">
            Remember
          </h4>
          <ul className="text-xs text-aqua-700 dark:text-aqua-400 space-y-1">
            <li>• Your journal is private and just for you</li>
            <li>• After saving, you can request AI insights on this entry</li>
            <li>• Write as much or as little as you need</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
