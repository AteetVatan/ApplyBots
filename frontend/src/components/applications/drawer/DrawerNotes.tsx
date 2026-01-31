/**
 * Notes section for the application detail drawer.
 */

"use client";

import { Trash2, Plus, Loader2, MessageSquareText } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import type { ApplicationNote } from "@/lib/api";

interface DrawerNotesProps {
  notes: ApplicationNote[];
  noteContent: string;
  onNoteContentChange: (value: string) => void;
  onAddNote: () => void;
  onDeleteNote: (noteId: string) => void;
  isAddingNote: boolean;
  isDeletingNote: boolean;
}

export function DrawerNotes({
  notes,
  noteContent,
  onNoteContentChange,
  onAddNote,
  onDeleteNote,
  isAddingNote,
  isDeletingNote,
}: DrawerNotesProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onAddNote();
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-neutral-400 uppercase tracking-wider flex items-center gap-2">
        <MessageSquareText className="w-4 h-4" />
        Notes ({notes.length})
      </h3>

      {/* Add note form */}
      <div className="flex gap-2">
        <input
          type="text"
          value={noteContent}
          onChange={(e) => onNoteContentChange(e.target.value)}
          placeholder="Add a note..."
          className="flex-1 px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-xl text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:border-primary-500/50 transition-colors"
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={onAddNote}
          disabled={!noteContent.trim() || isAddingNote}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-medium transition-colors flex items-center gap-2"
        >
          {isAddingNote ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Notes list */}
      <div className="space-y-2">
        {notes.length === 0 ? (
          <p className="text-sm text-neutral-500 py-4 text-center">
            No notes yet. Add one above!
          </p>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="p-3 bg-neutral-800/50 rounded-xl group">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm text-neutral-200 flex-1">{note.content}</p>
                <button
                  onClick={() => onDeleteNote(note.id)}
                  disabled={isDeletingNote}
                  className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-neutral-700 transition-all"
                >
                  <Trash2 className="w-4 h-4 text-neutral-500 hover:text-error-500" />
                </button>
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                {formatRelativeTime(note.created_at)}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
