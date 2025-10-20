/**
 * Journal main page - List and filter journal entries
 */

'use client';

import { useState, useEffect } from 'react';
import { useJournal } from '@/hooks/useJournal';
import { JournalList } from '@/components/journal/JournalList';
import {
  Search,
  Plus,
  Filter,
  X,
  Tag,
  Sparkles,
  TrendingUp,
  BookOpen,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { JournalInsightsResponse } from '@/lib/types/journal';

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

export default function JournalPage() {
  const router = useRouter();
  const [userId] = useState(getUserId);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [moodRange, setMoodRange] = useState<[number | null, number | null]>([null, null]);
  const [insights, setInsights] = useState<JournalInsightsResponse | null>(null);

  const {
    entries,
    total,
    page,
    pageSize,
    hasMore,
    isLoading,
    error,
    filters,
    loadEntries,
    deleteEntry,
    updateFilters,
    nextPage,
    previousPage,
    clearFilters,
    getInsights,
  } = useJournal({ userId, autoLoad: true });

  // Load insights on mount
  useEffect(() => {
    getInsights(30).then((data) => {
      if (data) setInsights(data);
    });
  }, [getInsights]);

  // Get all unique tags from entries
  const allTags = Array.from(new Set(entries.flatMap((entry) => entry.tags)));

  const handleSearch = () => {
    updateFilters({
      ...filters,
      search: searchQuery || undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      mood_min: moodRange[0] ?? undefined,
      mood_max: moodRange[1] ?? undefined,
    });
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedTags([]);
    setMoodRange([null, null]);
    clearFilters();
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleDelete = async (id: string) => {
    const success = await deleteEntry(id);
    if (success) {
      // Reload current page
      loadEntries();
    }
  };

  const hasActiveFilters = searchQuery || selectedTags.length > 0 || moodRange[0] !== null || moodRange[1] !== null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                <BookOpen className="w-7 h-7 text-aqua-500" />
                My Journal
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {total} {total === 1 ? 'entry' : 'entries'} total
              </p>
            </div>

            <button
              onClick={() => router.push('/journal/new')}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-aqua-500 to-ocean-500 text-white rounded-lg hover:from-aqua-600 hover:to-ocean-600 transition-all shadow-md hover:shadow-lg"
            >
              <Plus className="w-5 h-5" />
              New Entry
            </button>
          </div>

          {/* Search and Filters */}
          <div className="space-y-3">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search entries..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-aqua-500 dark:focus:ring-aqua-400 transition-all"
                />
              </div>

              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                  showFilters || hasActiveFilters
                    ? 'bg-aqua-50 dark:bg-aqua-950/20 border-aqua-500 text-aqua-700 dark:text-aqua-300'
                    : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Filter className="w-5 h-5" />
                Filters
                {hasActiveFilters && (
                  <span className="px-2 py-0.5 bg-aqua-500 text-white text-xs rounded-full">
                    {(selectedTags.length > 0 ? 1 : 0) + (moodRange[0] !== null || moodRange[1] !== null ? 1 : 0)}
                  </span>
                )}
              </button>

              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-aqua-500 text-white rounded-lg hover:bg-aqua-600 transition-colors"
              >
                Search
              </button>
            </div>

            {/* Filter Panel */}
            {showFilters && (
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 space-y-4 animate-slide-up">
                {/* Tags Filter */}
                {allTags.length > 0 && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                      <Tag className="w-4 h-4" />
                      Filter by tags
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {allTags.map((tag) => (
                        <button
                          key={tag}
                          onClick={() => handleTagToggle(tag)}
                          className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                            selectedTags.includes(tag)
                              ? 'bg-aqua-500 text-white border-aqua-500'
                              : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-aqua-400'
                          }`}
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Mood Range */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Mood range
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={moodRange[0] ?? ''}
                      onChange={(e) => setMoodRange([e.target.value ? Number(e.target.value) : null, moodRange[1]])}
                      placeholder="Min"
                      className="w-20 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-aqua-500"
                    />
                    <span className="text-gray-500">to</span>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={moodRange[1] ?? ''}
                      onChange={(e) => setMoodRange([moodRange[0], e.target.value ? Number(e.target.value) : null])}
                      placeholder="Max"
                      className="w-20 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-aqua-500"
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-2">
                  <button
                    onClick={handleClearFilters}
                    className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                  >
                    <X className="w-4 h-4" />
                    Clear all
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Insights Banner */}
      {insights && insights.entries_analyzed > 0 && (
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="p-4 bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 rounded-xl border border-aqua-200 dark:border-aqua-800">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-aqua-600 dark:text-aqua-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-aqua-800 dark:text-aqua-300 mb-1">
                  Your Journal Insights
                </h3>
                <div className="flex flex-wrap items-center gap-4 text-xs text-aqua-700 dark:text-aqua-400">
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    <span>
                      {insights.writing_streak > 0
                        ? `${insights.writing_streak} day writing streak!`
                        : 'Start your writing streak today'}
                    </span>
                  </div>
                  {insights.mood_trend && (
                    <div className="flex items-center gap-1">
                      <span>Mood trend: </span>
                      <span className="font-semibold capitalize">{insights.mood_trend}</span>
                    </div>
                  )}
                  <div>
                    {insights.entries_analyzed} entries analyzed in the last 30 days
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        </div>
      )}

      {/* Journal List */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        <JournalList
          entries={entries}
          total={total}
          page={page}
          pageSize={pageSize}
          hasMore={hasMore}
          onNextPage={nextPage}
          onPreviousPage={previousPage}
          onDeleteEntry={handleDelete}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}
