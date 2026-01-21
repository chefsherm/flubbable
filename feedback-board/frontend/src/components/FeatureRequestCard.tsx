'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { featureRequestsApi } from '@/lib/api';
import type { FeatureRequest } from '@/types';
import { useAuthStore } from '@/store/authStore';
import { formatDistanceToNow } from 'date-fns';

interface Props {
  request: FeatureRequest;
  userVotes: Set<string>;
}

export default function FeatureRequestCard({ request, userVotes }: Props) {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [isDeleting, setIsDeleting] = useState(false);
  const hasVoted = userVotes.has(request.id);

  const voteMutation = useMutation({
    mutationFn: () =>
      hasVoted
        ? featureRequestsApi.unvote(request.id)
        : featureRequestsApi.vote(request.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature-requests'] });
      queryClient.invalidateQueries({ queryKey: ['user-votes'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => featureRequestsApi.delete(request.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature-requests'] });
    },
  });

  const handleVote = () => {
    if (!user) return;
    voteMutation.mutate();
  };

  const handleDelete = async () => {
    if (!user?.isAdmin) return;

    if (window.confirm('Are you sure you want to delete this feature request?')) {
      setIsDeleting(true);
      try {
        await deleteMutation.mutateAsync();
      } catch (error) {
        console.error('Error deleting request:', error);
        alert('Failed to delete request');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex gap-4">
        {/* Vote button */}
        <div className="flex flex-col items-center gap-1">
          <button
            onClick={handleVote}
            disabled={!user || voteMutation.isPending}
            className={`flex flex-col items-center justify-center w-12 h-12 rounded-lg border-2 transition-colors ${
              hasVoted
                ? 'bg-primary-600 border-primary-600 text-white'
                : 'bg-white border-gray-300 text-gray-600 hover:border-primary-600 hover:text-primary-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
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
                d="M5 15l7-7 7 7"
              />
            </svg>
          </button>
          <span className="text-sm font-semibold text-gray-700">{request.votes}</span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {request.title}
          </h3>
          <p className="text-gray-600 mb-3 whitespace-pre-wrap">
            {request.description}
          </p>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>by {request.authorEmail}</span>
              <span>•</span>
              <span>{formatDistanceToNow(new Date(request.createdAt), { addSuffix: true })}</span>
            </div>

            {user?.isAdmin && (
              <button
                onClick={handleDelete}
                disabled={isDeleting || deleteMutation.isPending}
                className="btn btn-danger text-sm"
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
