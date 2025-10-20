/**
 * AIInsights component - Display AI analysis results for journal entries
 */

'use client';

import { useState } from 'react';
import {
  Sparkles,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  ChevronDown,
  ChevronUp,
  Brain,
  Heart,
} from 'lucide-react';
import { JournalAnalysisResponse, JournalInsight } from '@/lib/types/journal';

interface AIInsightsProps {
  analysis: JournalAnalysisResponse;
  isLoading?: boolean;
  className?: string;
}

const SENTIMENT_CONFIG = {
  positive: {
    color: 'from-green-500 to-emerald-500',
    bg: 'bg-green-50 dark:bg-green-950/20',
    border: 'border-green-200 dark:border-green-800',
    text: 'text-green-700 dark:text-green-300',
    icon: Heart,
    label: 'Positive',
  },
  neutral: {
    color: 'from-blue-500 to-cyan-500',
    bg: 'bg-blue-50 dark:bg-blue-950/20',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-700 dark:text-blue-300',
    icon: Brain,
    label: 'Neutral',
  },
  negative: {
    color: 'from-amber-500 to-orange-500',
    bg: 'bg-amber-50 dark:bg-amber-950/20',
    border: 'border-amber-200 dark:border-amber-800',
    text: 'text-amber-700 dark:text-amber-300',
    icon: AlertCircle,
    label: 'Needs attention',
  },
  mixed: {
    color: 'from-purple-500 to-pink-500',
    bg: 'bg-purple-50 dark:bg-purple-950/20',
    border: 'border-purple-200 dark:border-purple-800',
    text: 'text-purple-700 dark:text-purple-300',
    icon: Brain,
    label: 'Mixed',
  },
};

const SEVERITY_CONFIG = {
  low: {
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-100 dark:bg-blue-900/30',
  },
  medium: {
    color: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-100 dark:bg-amber-900/30',
  },
  high: {
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-100 dark:bg-red-900/30',
  },
};

function InsightCard({ insight }: { insight: JournalInsight }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const severityConfig = SEVERITY_CONFIG[insight.severity];

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-aqua-300 dark:hover:border-aqua-600 transition-all">
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${severityConfig.bg}`}>
          <Lightbulb className={`w-4 h-4 ${severityConfig.color}`} />
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div>
              <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200 capitalize">
                {insight.category}
              </h4>
              <span className={`text-xs ${severityConfig.color}`}>
                {insight.severity} priority
              </span>
            </div>
          </div>

          <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
            {insight.insight}
          </p>

          {insight.recommendations.length > 0 && (
            <div>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-1 text-xs text-aqua-600 dark:text-aqua-400 hover:text-aqua-700 dark:hover:text-aqua-300 transition-colors"
              >
                <span>
                  {isExpanded ? 'Hide' : 'Show'} recommendations ({insight.recommendations.length})
                </span>
                {isExpanded ? (
                  <ChevronUp className="w-3 h-3" />
                ) : (
                  <ChevronDown className="w-3 h-3" />
                )}
              </button>

              {isExpanded && (
                <ul className="mt-2 space-y-1 animate-slide-up">
                  {insight.recommendations.map((rec, idx) => (
                    <li
                      key={idx}
                      className="text-xs text-gray-600 dark:text-gray-400 pl-4 relative before:content-['•'] before:absolute before:left-0 before:text-aqua-500"
                    >
                      {rec}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function AIInsights({ analysis, isLoading = false, className = '' }: AIInsightsProps) {
  const sentimentConfig = SENTIMENT_CONFIG[analysis.sentiment];
  const SentimentIcon = sentimentConfig.icon;

  if (isLoading) {
    return (
      <div className={`p-6 bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 rounded-2xl border border-aqua-200 dark:border-aqua-800 ${className}`}>
        <div className="flex items-center gap-3 mb-4">
          <div className="animate-spin">
            <Sparkles className="w-6 h-6 text-aqua-500" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Analyzing your entry...
          </h3>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-20 bg-white/50 dark:bg-gray-800/50 rounded-xl animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header with Sentiment */}
      <div className={`p-6 bg-gradient-to-br ${sentimentConfig.color} rounded-2xl text-white shadow-lg`}>
        <div className="flex items-center gap-3 mb-2">
          <SentimentIcon className="w-6 h-6" />
          <h3 className="text-xl font-bold">AI Insights</h3>
        </div>
        <p className="text-sm opacity-90">
          Overall sentiment: <span className="font-semibold">{sentimentConfig.label}</span>
        </p>
      </div>

      {/* Themes */}
      {analysis.themes.length > 0 && (
        <div className="p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-aqua-500" />
            <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              Key Themes
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.themes.map((theme, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-gradient-to-br from-aqua-100 to-ocean-100 dark:from-aqua-900/30 dark:to-ocean-900/30 text-aqua-700 dark:text-aqua-300 text-sm rounded-full border border-aqua-300 dark:border-aqua-700 capitalize"
              >
                {theme}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Insights */}
      {analysis.insights.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <Brain className="w-4 h-4 text-aqua-500" />
            Detailed Insights
          </h4>
          {analysis.insights.map((insight, idx) => (
            <InsightCard key={idx} insight={insight} />
          ))}
        </div>
      )}

      {/* Suggestions */}
      {analysis.suggestions.length > 0 && (
        <div className={`p-4 ${sentimentConfig.bg} border ${sentimentConfig.border} rounded-xl`}>
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className={`w-4 h-4 ${sentimentConfig.text}`} />
            <h4 className={`text-sm font-semibold ${sentimentConfig.text}`}>
              Gentle Suggestions
            </h4>
          </div>
          <ul className="space-y-2">
            {analysis.suggestions.map((suggestion, idx) => (
              <li
                key={idx}
                className={`text-sm ${sentimentConfig.text} pl-4 relative before:content-['→'] before:absolute before:left-0`}
              >
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Footer note */}
      <p className="text-xs text-gray-500 dark:text-gray-400 text-center italic">
        These insights are AI-generated to support your reflection.
        Trust your own feelings and judgment.
      </p>
    </div>
  );
}
