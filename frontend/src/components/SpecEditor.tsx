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
  onGenerate: () => void;
}

interface SortableKUItemProps {
  ku: KnowledgeUnit;
  onEdit: (ku: KnowledgeUnit) => void;
  onDelete: (kuId: string) => void;
}

// Sortable KU Card component
const SortableKUItem: React.FC<SortableKUItemProps> = ({ ku, onEdit, onDelete }) => {
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
      className="bg-white border border-gray-200 rounded-lg p-4 mb-3 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {/* Drag handle */}
            <button
              {...attributes}
              {...listeners}
              className="cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600 p-1"
              aria-label="Drag to reorder"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8h16M4 16h16"
                />
              </svg>
            </button>
            <h3 className="text-lg font-semibold text-gray-900">{ku.title}</h3>
          </div>
          <p className="text-sm text-gray-600 mb-3 ml-7">{ku.description}</p>
          {ku.learning_objectives && ku.learning_objectives.length > 0 && (
            <div className="ml-7">
              <h4 className="text-xs font-semibold text-gray-700 mb-1">
                Learning Objectives:
              </h4>
              <ul className="text-xs text-gray-600 list-disc list-inside space-y-1">
                {ku.learning_objectives.map((obj, idx) => (
                  <li key={idx}>{obj}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <div className="flex gap-2 ml-4">
          <button
            onClick={() => onEdit(ku)}
            className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
            aria-label="Edit knowledge unit"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(ku.id)}
            className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
            aria-label="Delete knowledge unit"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export const SpecEditor: React.FC<SpecEditorProps> = ({ spec, onUpdate, onGenerate }) => {
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
    <div className="mt-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900 mb-1">Document Specification</h2>
        <p className="text-sm text-gray-600">
          Topic: <span className="font-medium">{spec.topic}</span>
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {spec.knowledge_units.length} knowledge unit
          {spec.knowledge_units.length !== 1 ? 's' : ''}
        </p>
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
          <div className="space-y-3">
            {spec.knowledge_units.map((ku) => (
              <SortableKUItem
                key={ku.id}
                ku={ku}
                onEdit={handleEditKU}
                onDelete={handleDeleteKU}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {spec.knowledge_units.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No knowledge units in this specification.</p>
        </div>
      )}

      <button
        onClick={onGenerate}
        disabled={spec.knowledge_units.length === 0}
        className="mt-6 w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Generate Document
      </button>

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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Edit Knowledge Unit</h2>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label
                  htmlFor="title"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="description"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="objectives"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Learning Objectives (one per line)
                </label>
                <textarea
                  id="objectives"
                  value={objectives}
                  onChange={(e) => setObjectives(e.target.value)}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter each learning objective on a new line"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
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
