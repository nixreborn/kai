/**
 * Custom hook for journal state management and operations
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import {
  JournalEntry,
  JournalEntryCreate,
  JournalEntryUpdate,
  JournalListParams,
  JournalAnalysisResponse,
  JournalInsightsResponse,
  JournalPromptsResponse,
} from '@/lib/types/journal';
import {
  createJournalEntry,
  listJournalEntries,
  getJournalEntry,
  updateJournalEntry,
  deleteJournalEntry,
  analyzeJournalEntry,
  getJournalPrompts,
  getJournalInsights,
} from '@/lib/api/journal';

interface UseJournalOptions {
  userId: string;
  autoLoad?: boolean;
  initialParams?: JournalListParams;
}

export function useJournal({ userId, autoLoad = true, initialParams }: UseJournalOptions) {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [currentEntry, setCurrentEntry] = useState<JournalEntry | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialParams?.page || 1);
  const [pageSize] = useState(initialParams?.page_size || 20);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<JournalListParams>(initialParams || {});

  /**
   * Load entries with current filters and pagination
   */
  const loadEntries = useCallback(
    async (params?: JournalListParams) => {
      setIsLoading(true);
      setError(null);

      try {
        const requestParams = {
          ...filters,
          ...params,
          page: params?.page || page,
          page_size: pageSize,
        };

        const result = await listJournalEntries(userId, requestParams);
        setEntries(result.entries);
        setTotal(result.total);
        setPage(result.page);
        setHasMore(result.has_more);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load journal entries';
        setError(message);
        console.error('Error loading journal entries:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, filters, page, pageSize]
  );

  /**
   * Load a specific entry by ID
   */
  const loadEntry = useCallback(
    async (entryId: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const entry = await getJournalEntry(userId, entryId);
        setCurrentEntry(entry);
        return entry;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load journal entry';
        setError(message);
        console.error('Error loading journal entry:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [userId]
  );

  /**
   * Create a new journal entry
   */
  const createEntry = useCallback(
    async (entry: JournalEntryCreate) => {
      setIsLoading(true);
      setError(null);

      try {
        const newEntry = await createJournalEntry(userId, entry);
        // Refresh the list
        await loadEntries();
        return newEntry;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create journal entry';
        setError(message);
        console.error('Error creating journal entry:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, loadEntries]
  );

  /**
   * Update an existing journal entry
   */
  const updateEntry = useCallback(
    async (entryId: string, updates: JournalEntryUpdate) => {
      setIsLoading(true);
      setError(null);

      try {
        const updatedEntry = await updateJournalEntry(userId, entryId, updates);

        // Update in the list if present
        setEntries((prev) =>
          prev.map((e) => (e.id === entryId ? updatedEntry : e))
        );

        // Update current entry if it's the one being edited
        if (currentEntry?.id === entryId) {
          setCurrentEntry(updatedEntry);
        }

        return updatedEntry;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update journal entry';
        setError(message);
        console.error('Error updating journal entry:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, currentEntry]
  );

  /**
   * Delete a journal entry
   */
  const deleteEntry = useCallback(
    async (entryId: string) => {
      setIsLoading(true);
      setError(null);

      try {
        await deleteJournalEntry(userId, entryId);

        // Remove from list
        setEntries((prev) => prev.filter((e) => e.id !== entryId));

        // Clear current entry if it was deleted
        if (currentEntry?.id === entryId) {
          setCurrentEntry(null);
        }

        setTotal((prev) => prev - 1);
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to delete journal entry';
        setError(message);
        console.error('Error deleting journal entry:', err);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, currentEntry]
  );

  /**
   * Analyze a journal entry with AI
   */
  const analyzeEntry = useCallback(
    async (entryId: string): Promise<JournalAnalysisResponse | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const analysis = await analyzeJournalEntry(userId, entryId);

        // Update the entry with new insights
        if (currentEntry?.id === entryId) {
          const updatedEntry = await getJournalEntry(userId, entryId);
          setCurrentEntry(updatedEntry);
        }

        return analysis;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to analyze journal entry';
        setError(message);
        console.error('Error analyzing journal entry:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, currentEntry]
  );

  /**
   * Get AI-generated writing prompts
   */
  const getPrompts = useCallback(async (): Promise<JournalPromptsResponse | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const prompts = await getJournalPrompts(userId);
      return prompts;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get journal prompts';
      setError(message);
      console.error('Error getting journal prompts:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  /**
   * Get wellness insights from journal history
   */
  const getInsights = useCallback(
    async (days: number = 30): Promise<JournalInsightsResponse | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const insights = await getJournalInsights(userId, days);
        return insights;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to get journal insights';
        setError(message);
        console.error('Error getting journal insights:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [userId]
  );

  /**
   * Update filters and reload
   */
  const updateFilters = useCallback(
    (newFilters: JournalListParams) => {
      setFilters(newFilters);
      setPage(1);
      loadEntries({ ...newFilters, page: 1 });
    },
    [loadEntries]
  );

  /**
   * Go to next page
   */
  const nextPage = useCallback(() => {
    if (hasMore) {
      const newPage = page + 1;
      setPage(newPage);
      loadEntries({ page: newPage });
    }
  }, [hasMore, page, loadEntries]);

  /**
   * Go to previous page
   */
  const previousPage = useCallback(() => {
    if (page > 1) {
      const newPage = page - 1;
      setPage(newPage);
      loadEntries({ page: newPage });
    }
  }, [page, loadEntries]);

  /**
   * Clear all filters
   */
  const clearFilters = useCallback(() => {
    setFilters({});
    setPage(1);
    loadEntries({ page: 1 });
  }, [loadEntries]);

  // Auto-load on mount if enabled
  useEffect(() => {
    if (autoLoad) {
      loadEntries();
    }
  }, [autoLoad]); // Only run on mount

  return {
    // State
    entries,
    currentEntry,
    total,
    page,
    pageSize,
    hasMore,
    isLoading,
    error,
    filters,

    // Actions
    loadEntries,
    loadEntry,
    createEntry,
    updateEntry,
    deleteEntry,
    analyzeEntry,
    getPrompts,
    getInsights,
    updateFilters,
    nextPage,
    previousPage,
    clearFilters,
    setCurrentEntry,
  };
}
