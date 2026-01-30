import React, { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { DocumentSpec, KnowledgeUnit } from '../types/models';

interface SpecEditorProps {
  spec: DocumentSpec;
  onUpdate: (spec: DocumentSpec) => void;
}

interface SortableKUItemProps {
  ku: KnowledgeUnit;
  onEdit: (ku: KnowledgeUnit) => void;
  onDelete: (kuId: string) => void;
}

// Sortable KU Card component
const SortableKUItem: React.FC<SortableKUItemProps & { index: number }> = ({ ku, index, onEdit, onDelete }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: ku.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="glass-card rounded-xl border border-[var(--border-color)] bg-[var(--surface-color)] p-3 mb-3 group hover:shadow-md transition-all relative overflow-hidden"
    >
      {/* Decorative gradient overlay */}
      <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500 opacity-80" />

      <div className="flex items-center justify-between pl-3">
        <div className="flex-1 flex items-center gap-3">
          {/* Drag handle */}
          <button
            {...attributes}
            {...listeners}
            className="cursor-grab active:cursor-grabbing text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
            aria-label="Drag to reorder"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
            </svg>
          </button>

          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-[var(--accent-primary)] uppercase tracking-wider mb-0.5">
              KU({index + 1})
            </span>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] leading-tight line-clamp-2">
              {ku.title}
            </h3>
          </div>
        </div>

        <div className="flex flex-col gap-1 ml-2 border-l border-[var(--border-color)] pl-2">
          <button
            onClick={() => onEdit(ku)}
            className="p-1.5 text-[var(--text-secondary)] hover:text-indigo-600 hover:bg-indigo-50/50 rounded-md transition-colors"
            aria-label="Edit"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" /><path d="m15 5 4 4" /></svg>
          </button>
          <button
            onClick={() => onDelete(ku.id)}
            className="p-1.5 text-[var(--text-secondary)] hover:text-red-600 hover:bg-red-50/50 rounded-md transition-colors"
            aria-label="Delete"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /><line x1="10" x2="10" y1="11" y2="17" /><line x1="14" x2="14" y1="11" y2="17" /></svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export const SpecEditor: React.FC<SpecEditorProps> = ({ spec, onUpdate }) => {
  const [editingKU, setEditingKU] = useState<KnowledgeUnit | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = spec.knowledge_units.findIndex((ku) => ku.id === active.id);
      const newIndex = spec.knowledge_units.findIndex((ku) => ku.id === over.id);

      const reorderedKUs = arrayMove(spec.knowledge_units, oldIndex, newIndex);
      const updatedSpec = {
        ...spec,
        knowledge_units: reorderedKUs,
      };
      onUpdate(updatedSpec);
    }
  };

  const handleEditKU = (ku: KnowledgeUnit) => {
    setEditingKU(ku);
  };

  const handleDeleteKU = (kuId: string) => {
    const updatedSpec = {
      ...spec,
      knowledge_units: spec.knowledge_units.filter((ku) => ku.id !== kuId),
    };
    onUpdate(updatedSpec);
  };

  const handleSaveKU = (updatedKU: KnowledgeUnit) => {
    const updatedSpec = {
      ...spec,
      knowledge_units: spec.knowledge_units.map((ku) =>
        ku.id === updatedKU.id ? updatedKU : ku
      ),
    };
    onUpdate(updatedSpec);
    setEditingKU(null);
  };

  const handleCloseModal = () => {
    setEditingKU(null);
  };

  return (
    <div className="mt-2">
      <div className="mb-6 px-1">
        <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-1">Specification</h2>
        <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
          <span className="bg-[var(--surface-color)] border border-[var(--border-color)] px-2 py-0.5 rounded text-[var(--text-secondary)] font-mono">
            {spec.knowledge_units.length} unit{spec.knowledge_units.length !== 1 ? 's' : ''}
          </span>
          <span>•</span>
          <span className="truncate max-w-[150px] font-medium">{spec.topic}</span>
        </div>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={spec.knowledge_units.map((ku) => ku.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-1">
            {spec.knowledge_units.map((ku, index) => (
              <SortableKUItem
                key={ku.id}
                ku={ku}
                index={index}
                onEdit={handleEditKU}
                onDelete={handleDeleteKU}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {spec.knowledge_units.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          <p>No knowledge units in this specification.</p>
        </div>
      )}

      {/* Button moved to sidebar footer */}

      {/* Edit Modal */}
      {editingKU && (
        <KUEditModal
          ku={editingKU}
          onSave={handleSaveKU}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

// KU Edit Modal Component
interface KUEditModalProps {
  ku: KnowledgeUnit;
  onSave: (ku: KnowledgeUnit) => void;
  onClose: () => void;
}

const KUEditModal: React.FC<KUEditModalProps> = ({ ku, onSave, onClose }) => {
  const [title, setTitle] = useState(ku.title);
  const [description, setDescription] = useState(ku.description);
  const [objectives, setObjectives] = useState(
    (ku.learning_objectives || []).join('\n')
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const updatedKU: KnowledgeUnit = {
      ...ku,
      title: title.trim(),
      description: description.trim(),
      learning_objectives: objectives
        .split('\n')
        .map((obj) => obj.trim())
        .filter((obj) => obj.length > 0),
    };
    onSave(updatedKU);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-panel w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl shadow-2xl border border-white/10">
        <div className="p-6">
          <h2 className="text-xl font-bold text-white mb-6">Edit Knowledge Unit</h2>
          <form onSubmit={handleSubmit}>
            <div className="space-y-5">
              <div>
                <label
                  htmlFor="title"
                  className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2"
                >
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-700 text-zinc-100 rounded-xl focus:outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10 transition-all"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="description"
                  className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2"
                >
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-700 text-zinc-100 rounded-xl focus:outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10 transition-all resize-none"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="objectives"
                  className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2"
                >
                  Learning Objectives (one per line)
                </label>
                <textarea
                  id="objectives"
                  value={objectives}
                  onChange={(e) => setObjectives(e.target.value)}
                  rows={6}
                  className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-700 text-zinc-100 rounded-xl focus:outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10 transition-all font-mono text-sm resize-none"
                  placeholder="Enter each learning objective on a new line"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-8 pt-6 border-t border-white/5">
              <button
                type="submit"
                className="flex-1 btn-primary py-2.5 px-4 rounded-xl font-semibold transition-all active:scale-[0.98]"
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-semibold py-2.5 px-4 rounded-xl transition-colors border border-white/5"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SpecEditor;
