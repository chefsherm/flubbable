'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { featureRequestsApi } from '@/lib/api';

export default function CreateFeatureRequestForm() {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: featureRequestsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature-requests'] });
      setTitle('');
      setDescription('');
      setIsOpen(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && description.trim()) {
      createMutation.mutate({ title: title.trim(), description: description.trim() });
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn btn-primary w-full"
      >
        + Create Feature Request
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        New Feature Request
      </h3>

      <div className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Brief description of the feature"
            className="input"
            required
            maxLength={200}
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Provide more details about your feature request"
            className="textarea"
            rows={4}
            required
            maxLength={2000}
          />
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={createMutation.isPending || !title.trim() || !description.trim()}
            className="btn btn-primary flex-1"
          >
            {createMutation.isPending ? 'Creating...' : 'Submit'}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsOpen(false);
              setTitle('');
              setDescription('');
            }}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        </div>

        {createMutation.isError && (
          <p className="text-red-600 text-sm">
            Failed to create request. Please try again.
          </p>
        )}
      </div>
    </form>
  );
}
