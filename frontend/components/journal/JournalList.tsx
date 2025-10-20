/**
 * JournalList component - List of journal entries with pagination and date grouping
 */

'use client';

import { JournalEntry } from '@/lib/types/journal';
import { JournalEntryCard } from './JournalEntryCard';
import { ChevronLeft, ChevronRight, BookOpen } from 'lucide-react';

interface JournalListProps {
  entries: JournalEntry[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
  onNextPage?: () => void;
  onPreviousPage?: () => void;
  onDeleteEntry?: (id: string) => void;
  isLoading?: boolean;
}

function groupEntriesByDate(entries: JournalEntry[]) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const thisWeekStart = new Date(today);
  thisWeekStart.setDate(thisWeekStart.getDate() - 7);

  const thisMonthStart = new Date(today);
  thisMonthStart.setDate(thisMonthStart.getDate() - 30);

  const groups: { [key: string]: JournalEntry[] } = {
    Today: [],
    Yesterday: [],
    'This Week': [],
    'This Month': [],
    Older: [],
  };

  entries.forEach((entry) => {
    const entryDate = new Date(entry.created_at);
    entryDate.setHours(0, 0, 0, 0);

    if (entryDate.getTime() === today.getTime()) {
      groups.Today.push(entry);
    } else if (entryDate.getTime() === yesterday.getTime()) {
      groups.Yesterday.push(entry);
    } else if (entryDate >= thisWeekStart) {
      groups['This Week'].push(entry);
    } else if (entryDate >= thisMonthStart) {
      groups['This Month'].push(entry);
    } else {
      groups.Older.push(entry);
    }
  });

  // Remove empty groups
  return Object.entries(groups).filter(([_, entries]) => entries.length > 0);
}

export function JournalList({
  entries,
  total,
  page,
  pageSize,
  hasMore,
  onNextPage,
  onPreviousPage,
  onDeleteEntry,
  isLoading = false,
}: JournalListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-48 bg-gray-100 dark:bg-gray-800 rounded-xl animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-aqua-500 to-ocean-500 flex items-center justify-center mb-4 shadow-lg">
          <BookOpen className="w-10 h-10 text-white" />
        </div>
        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          No entries found
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md mb-6">
          Start your journaling journey by creating your first entry.
          Writing helps you reflect and grow.
        </p>
      </div>
    );
  }

  const groupedEntries = groupEntriesByDate(entries);
  const startIndex = (page - 1) * pageSize + 1;
  const endIndex = Math.min(page * pageSize, total);

  return (
    <div className="space-y-8">
      {/* Grouped entries */}
      {groupedEntries.map(([groupName, groupEntries]) => (
        <div key={groupName} className="space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
              {groupName}
            </h2>
            <div className="h-px flex-1 bg-gradient-to-r from-aqua-200 to-transparent dark:from-aqua-800" />
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {groupEntries.length} {groupEntries.length === 1 ? 'entry' : 'entries'}
            </span>
          </div>

          <div className="grid gap-4">
            {groupEntries.map((entry) => (
              <JournalEntryCard
                key={entry.id}
                entry={entry}
                onDelete={onDeleteEntry}
              />
            ))}
          </div>
        </div>
      ))}

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Showing {startIndex}–{endIndex} of {total} entries
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onPreviousPage}
              disabled={page === 1}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </button>

            <div className="flex items-center gap-1">
              {Array.from({ length: Math.ceil(total / pageSize) }, (_, i) => i + 1)
                .filter((p) => {
                  // Show first page, last page, current page, and pages around current
                  return (
                    p === 1 ||
                    p === Math.ceil(total / pageSize) ||
                    Math.abs(p - page) <= 1
                  );
                })
                .map((p, idx, arr) => {
                  // Add ellipsis if there's a gap
                  const showEllipsis = idx > 0 && arr[idx - 1] !== p - 1;

                  return (
                    <div key={p} className="flex items-center">
                      {showEllipsis && (
                        <span className="px-2 text-gray-400 dark:text-gray-600">...</span>
                      )}
                      <button
                        onClick={() => {
                          if (p > page && onNextPage) onNextPage();
                          if (p < page && onPreviousPage) onPreviousPage();
                        }}
                        className={`w-10 h-10 text-sm font-medium rounded-lg transition-colors ${
                          p === page
                            ? 'bg-aqua-500 text-white'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                        }`}
                      >
                        {p}
                      </button>
                    </div>
                  );
                })}
            </div>

            <button
              onClick={onNextPage}
              disabled={!hasMore}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
