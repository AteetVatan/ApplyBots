/**
 * AI Assistant Summary generation mode.
 */

"use client";

import { Sparkles, Loader2, CheckCircle2 } from "lucide-react";

interface SummaryModeProps {
    isLoading: boolean;
    generatedSummary: string;
    onGenerate: () => void;
    onApply: () => void;
}

export function SummaryMode({
    isLoading,
    generatedSummary,
    onGenerate,
    onApply,
}: SummaryModeProps) {
    return (
        <div className="space-y-4">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="font-medium text-blue-800 dark:text-blue-300 mb-1">
                    Generate Professional Summary
                </h3>
                <p className="text-sm text-blue-600 dark:text-blue-400">
                    AI will analyze your experience and skills to create a compelling summary.
                </p>
            </div>

            <button
                onClick={onGenerate}
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50"
            >
                {isLoading ? (
                    <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Generating...
                    </>
                ) : (
                    <>
                        <Sparkles className="h-4 w-4" />
                        Generate Summary
                    </>
                )}
            </button>

            {generatedSummary && (
                <div className="space-y-3">
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                            {generatedSummary}
                        </p>
                    </div>
                    <button
                        onClick={onApply}
                        className="w-full flex items-center justify-center gap-2 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                    >
                        <CheckCircle2 className="h-4 w-4" />
                        Apply to Resume
                    </button>
                </div>
            )}
        </div>
    );
}
