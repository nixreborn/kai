/**
 * Single Journal Entry page - View and edit a journal entry with AI insights
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useJournal } from '@/hooks/useJournal';
import { JournalEditor } from '@/components/journal/JournalEditor';
import { TagManager } from '@/components/journal/TagManager';
import { AIInsights } from '@/components/journal/AIInsights';
import {
  Save,
  ArrowLeft,
  Trash2,
  Sparkles,
  Edit,
  Eye,
  Calendar,
} from 'lucide-react';
import { JournalAnalysisResponse } from '@/lib/types/journal';

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

export default function JournalEntryPage() {
  const params = useParams();
  const router = useRouter();
  const entryId = params.id as string;
  const [userId] = useState(getUserId);

  const {
    currentEntry,
    loadEntry,
    updateEntry,
    deleteEntry,
    analyzeEntry,
    isLoading,
    error,
  } = useJournal({ userId, autoLoad: false });

  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [mood, setMood] = useState<number | null>(null);
  const [moodEmoji, setMoodEmoji] = useState<string | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [analysis, setAnalysis] = useState<JournalAnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Load entry on mount
  useEffect(() => {
    if (entryId) {
      loadEntry(entryId);
    }
  }, [entryId, loadEntry]);

  // Update local state when entry loads
  useEffect(() => {
    if (currentEntry) {
      setTitle(currentEntry.title || '');
      setContent(currentEntry.content);
      setMood(currentEntry.mood);
      setMoodEmoji(currentEntry.mood_emoji);
      setTags(currentEntry.tags);

      // If entry has existing analysis, show it
      if (currentEntry.ai_insights) {
        // Convert stored insights to analysis format for display
        setAnalysis({
          insights: currentEntry.ai_insights.insights.map(i => ({
            category: i.category,
            insight: i.insight,
            severity: i.severity as 'low' | 'medium' | 'high',
            recommendations: [],
            time_period: 'This entry',
          })),
          sentiment: currentEntry.ai_insights.sentiment,
          themes: currentEntry.ai_insights.themes,
          suggestions: [],
        });
      }
    }
  }, [currentEntry]);

  const handleMoodChange = (newMood: number | null, emoji: string | null) => {
    setMood(newMood);
    setMoodEmoji(emoji);
  };

  const handleSave = async () => {
    if (!content.trim()) {
      alert('Content cannot be empty.');
      return;
    }

    setIsSaving(true);
    try {
      const updated = await updateEntry(entryId, {
        title: title.trim() || null,
        content: content.trim(),
        mood,
        mood_emoji: moodEmoji,
        tags,
      });

      if (updated) {
        setIsEditing(false);
      }
    } catch (err) {
      console.error('Error saving entry:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this entry? This cannot be undone.')) {
      return;
    }

    const success = await deleteEntry(entryId);
    if (success) {
      router.push('/journal');
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await analyzeEntry(entryId);
      if (result) {
        setAnalysis(result);
      }
    } catch (err) {
      console.error('Error analyzing entry:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCancelEdit = () => {
    if (currentEntry) {
      setTitle(currentEntry.title || '');
      setContent(currentEntry.content);
      setMood(currentEntry.mood);
      setMoodEmoji(currentEntry.mood_emoji);
      setTags(currentEntry.tags);
    }
    setIsEditing(false);
  };

  if (isLoading && !currentEntry) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-aqua-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading entry...</p>
        </div>
      </div>
    );
  }

  if (!currentEntry) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
            Entry not found
          </h2>
          <button
            onClick={() => router.push('/journal')}
            className="text-aqua-600 dark:text-aqua-400 hover:underline"
          >
            Go back to journal
          </button>
        </div>
      </div>
    );
  }

  const formattedDate = new Date(currentEntry.created_at).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const formattedTime = new Date(currentEntry.created_at).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push('/journal')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                aria-label="Go back"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  {isEditing ? 'Edit Entry' : 'Journal Entry'}
                </h1>
                <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                  <Calendar className="w-3 h-3" />
                  <span>{formattedDate} at {formattedTime}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isEditing ? (
                <>
                  <button
                    onClick={handleCancelEdit}
                    disabled={isSaving}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={isSaving || !content.trim()}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-aqua-500 to-ocean-500 text-white rounded-lg hover:from-aqua-600 hover:to-ocean-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  >
                    <Save className="w-4 h-4" />
                    {isSaving ? 'Saving...' : 'Save'}
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={handleDelete}
                    className="flex items-center gap-2 px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div className="max-w-5xl mx-auto px-4 pt-4">
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Entry Content */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              {isEditing ? (
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
              ) : (
                <div className="space-y-4">
                  {/* Title */}
                  {currentEntry.title && (
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                      {currentEntry.title}
                    </h2>
                  )}

                  {/* Mood */}
                  {currentEntry.mood && (
                    <div className="flex items-center gap-2 pb-3 border-b border-gray-200 dark:border-gray-700">
                      {currentEntry.mood_emoji && (
                        <span className="text-2xl">{currentEntry.mood_emoji}</span>
                      )}
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Mood: {currentEntry.mood}/10
                      </span>
                    </div>
                  )}

                  {/* Content */}
                  <div className="prose dark:prose-invert max-w-none">
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {currentEntry.content}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Tags */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Tags
              </h3>
              <TagManager
                tags={tags}
                onTagsChange={setTags}
                disabled={!isEditing || isSaving}
              />
            </div>

            {/* AI Analysis Section */}
            {analysis && !isEditing && (
              <AIInsights analysis={analysis} isLoading={isAnalyzing} />
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* AI Analysis Button */}
            {!isEditing && (
              <div className="bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 border border-aqua-200 dark:border-aqua-800 rounded-xl p-4">
                <div className="flex items-start gap-3 mb-3">
                  <Sparkles className="w-5 h-5 text-aqua-600 dark:text-aqua-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-aqua-800 dark:text-aqua-300 mb-1">
                      AI Insights
                    </h3>
                    <p className="text-xs text-aqua-700 dark:text-aqua-400">
                      Get personalized insights and patterns from this entry
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-aqua-500 to-ocean-500 text-white rounded-lg hover:from-aqua-600 hover:to-ocean-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                >
                  <Sparkles className="w-4 h-4" />
                  {isAnalyzing
                    ? 'Analyzing...'
                    : analysis
                    ? 'Refresh Insights'
                    : 'Analyze Entry'}
                </button>
              </div>
            )}

            {/* Entry Stats */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Entry Info
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Created</span>
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {formattedDate}
                  </span>
                </div>
                {currentEntry.updated_at !== currentEntry.created_at && (
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Last edited</span>
                    <span className="text-gray-700 dark:text-gray-300 font-medium">
                      {new Date(currentEntry.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Word count</span>
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {currentEntry.content.split(/\s+/).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Characters</span>
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {currentEntry.content.length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
