/**
 * Detail drawer for viewing and managing application details.
 */

"use client";

import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { motion, AnimatePresence } from "framer-motion";
import { X, Building2 } from "lucide-react";
import { getStatusColor, getMatchScoreColor } from "@/lib/utils";
import {
  useAddNote,
  useDeleteNote,
  useApproveApplication,
} from "@/hooks/useApplications";
import { DrawerTimeline, DrawerNotes, DrawerFooter } from "./drawer";
import type { Application, ApplicationStage } from "@/lib/api";

interface DetailDrawerProps {
  application: Application | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const STAGE_LABELS: Record<ApplicationStage, string> = {
  saved: "Saved",
  applied: "Applied",
  interviewing: "Interviewing",
  offer: "Offer",
  rejected: "Rejected",
};

export function DetailDrawer({
  application,
  open,
  onOpenChange,
}: DetailDrawerProps) {
  const [noteContent, setNoteContent] = useState("");
  const addNote = useAddNote();
  const deleteNote = useDeleteNote();
  const approveApplication = useApproveApplication();

  const handleAddNote = async () => {
    if (!application || !noteContent.trim()) return;
    await addNote.mutateAsync({
      applicationId: application.id,
      content: noteContent.trim(),
    });
    setNoteContent("");
  };

  const handleDeleteNote = async (noteId: string) => {
    if (!application) return;
    await deleteNote.mutateAsync({
      applicationId: application.id,
      noteId,
    });
  };

  const handleApprove = async () => {
    if (!application) return;
    await approveApplication.mutateAsync(application.id);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              />
            </Dialog.Overlay>

            <Dialog.Content asChild>
              <motion.div
                className="fixed right-0 top-0 h-full w-full max-w-lg bg-neutral-900 border-l border-neutral-800 shadow-2xl z-50 overflow-hidden flex flex-col"
                initial={{ x: "100%" }}
                animate={{ x: 0 }}
                exit={{ x: "100%" }}
                transition={{ type: "spring", damping: 25, stiffness: 300 }}
              >
                {application && (
                  <>
                    {/* Header */}
                    <div className="p-6 border-b border-neutral-800">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <Dialog.Title className="text-xl font-display font-bold text-neutral-100 mb-1">
                            {application.job_title}
                          </Dialog.Title>
                          <div className="flex items-center gap-2 text-neutral-400">
                            <Building2 className="w-4 h-4" />
                            <span>{application.company}</span>
                          </div>
                        </div>
                        <Dialog.Close asChild>
                          <button className="p-2 rounded-xl hover:bg-neutral-800 transition-colors">
                            <X className="w-5 h-5 text-neutral-400" />
                          </button>
                        </Dialog.Close>
                      </div>

                      {/* Badges */}
                      <div className="flex flex-wrap items-center gap-2 mt-4">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}
                        >
                          {application.status.replace("_", " ")}
                        </span>
                        <span className="px-3 py-1 rounded-full text-sm font-medium bg-neutral-800 text-neutral-300">
                          {STAGE_LABELS[application.stage]}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(application.match_score)} bg-neutral-800`}
                        >
                          {application.match_score}% match
                        </span>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-6">
                      <DrawerTimeline
                        createdAt={application.created_at}
                        submittedAt={application.submitted_at}
                        stageUpdatedAt={application.stage_updated_at}
                      />
                      <DrawerNotes
                        notes={application.notes}
                        noteContent={noteContent}
                        onNoteContentChange={setNoteContent}
                        onAddNote={handleAddNote}
                        onDeleteNote={handleDeleteNote}
                        isAddingNote={addNote.isPending}
                        isDeletingNote={deleteNote.isPending}
                      />
                    </div>

                    {/* Footer */}
                    <DrawerFooter
                      jobId={application.job_id}
                      status={application.status}
                      onApprove={handleApprove}
                      isApproving={approveApplication.isPending}
                    />
                  </>
                )}
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
}
