'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { featureRequestsApi } from '@/lib/api';
import api from '@/lib/api';
import Header from '@/components/Header';
import FeatureRequestCard from '@/components/FeatureRequestCard';
import CreateFeatureRequestForm from '@/components/CreateFeatureRequestForm';

export default function HomePage() {
  const { user, loading: authLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const { data: requests = [], isLoading: requestsLoading } = useQuery({
    queryKey: ['feature-requests'],
    queryFn: featureRequestsApi.getAll,
    enabled: !!user,
  });

  const { data: userVotesData = [] } = useQuery({
    queryKey: ['user-votes'],
    queryFn: async () => {
      const response = await api.get('/votes/me');
      return response.data;
    },
    enabled: !!user,
  });

  // Create a set of request IDs that the user has voted on
  const userVotes = new Set(userVotesData.map((vote: any) => vote.request_id));

  // Sort requests by votes (descending)
  const sortedRequests = [...requests].sort((a, b) => b.votes - a.votes);

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <CreateFeatureRequestForm />
        </div>

        {requestsLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading feature requests...</p>
          </div>
        ) : sortedRequests.length === 0 ? (
          <div className="card text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No feature requests yet</h3>
            <p className="mt-1 text-gray-500">Be the first to create one!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {sortedRequests.map((request) => (
              <FeatureRequestCard
                key={request.id}
                request={request}
                userVotes={userVotes}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
