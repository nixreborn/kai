/**
 * JournalEntryCard component - Preview card for journal entries
 */

'use client';

import { JournalEntry } from '@/lib/types/journal';
import { Calendar, Tag, Trash2, Edit, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface JournalEntryCardProps {
  entry: JournalEntry;
  onDelete?: (id: string) => void;
  showActions?: boolean;
}

export function JournalEntryCard({
  entry,
  onDelete,
  showActions = true
}: JournalEntryCardProps) {
  const router = useRouter();

  const formattedDate = new Date(entry.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const formattedTime = new Date(entry.created_at).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });

  // Truncate content for preview
  const previewContent = entry.content.length > 200
    ? entry.content.substring(0, 200) + '...'
    : entry.content;

  const handleClick = () => {
    router.push(`/journal/${entry.id}`);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && confirm('Are you sure you want to delete this entry?')) {
      onDelete(entry.id);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push(`/journal/${entry.id}`);
  };

  return (
    <div
      onClick={handleClick}
      className="group p-5 bg-white dark:bg-gray-900 rounded-xl border-2 border-gray-200 dark:border-gray-800 hover:border-aqua-400 dark:hover:border-aqua-600 transition-all duration-200 cursor-pointer hover:shadow-lg animate-fade-in"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {entry.mood_emoji && (
              <span className="text-2xl">{entry.mood_emoji}</span>
            )}
            {entry.title && (
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 line-clamp-1">
                {entry.title}
              </h3>
            )}
            {entry.ai_insights && (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-aqua-100 to-ocean-100 dark:from-aqua-900/30 dark:to-ocean-900/30 rounded-full">
                <Sparkles className="w-3 h-3 text-aqua-600 dark:text-aqua-400" />
                <span className="text-xs text-aqua-700 dark:text-aqua-300 font-medium">
                  Analyzed
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              <span>{formattedDate}</span>
            </div>
            <span>•</span>
            <span>{formattedTime}</span>
            {entry.mood && (
              <>
                <span>•</span>
                <span className="font-medium">Mood: {entry.mood}/10</span>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleEdit}
              className="p-2 hover:bg-aqua-50 dark:hover:bg-aqua-950/20 rounded-lg transition-colors"
              aria-label="Edit entry"
              title="Edit"
            >
              <Edit className="w-4 h-4 text-gray-600 dark:text-gray-400 hover:text-aqua-600 dark:hover:text-aqua-400" />
            </button>
            <button
              onClick={handleDelete}
              className="p-2 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition-colors"
              aria-label="Delete entry"
              title="Delete"
            >
              <Trash2 className="w-4 h-4 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400" />
            </button>
          </div>
        )}
      </div>

      {/* Content Preview */}
      <p className="text-sm text-gray-700 dark:text-gray-300 mb-3 line-clamp-3 whitespace-pre-wrap">
        {previewContent}
      </p>

      {/* Tags */}
      {entry.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {entry.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2 py-1 bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 text-aqua-700 dark:text-aqua-300 text-xs rounded-full border border-aqua-200 dark:border-aqua-800"
            >
              <Tag className="w-3 h-3" />
              {tag}
            </span>
          ))}
          {entry.tags.length > 4 && (
            <span className="text-xs text-gray-500 dark:text-gray-400 self-center">
              +{entry.tags.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* AI Insights Preview */}
      {entry.ai_insights && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-xs">
            <span className="text-gray-600 dark:text-gray-400">Sentiment:</span>
            <span
              className={`px-2 py-0.5 rounded-full font-medium capitalize ${
                entry.ai_insights.sentiment === 'positive'
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                  : entry.ai_insights.sentiment === 'negative'
                  ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
                  : entry.ai_insights.sentiment === 'mixed'
                  ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
              }`}
            >
              {entry.ai_insights.sentiment}
            </span>
            {entry.ai_insights.themes.length > 0 && (
              <>
                <span className="text-gray-400">•</span>
                <span className="text-gray-600 dark:text-gray-400">
                  Themes: {entry.ai_insights.themes.slice(0, 2).join(', ')}
                  {entry.ai_insights.themes.length > 2 && '...'}
                </span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Read more indicator */}
      <div className="mt-3 text-xs text-aqua-600 dark:text-aqua-400 font-medium group-hover:text-aqua-700 dark:group-hover:text-aqua-300 transition-colors">
        Click to read more →
      </div>
    </div>
  );
}
