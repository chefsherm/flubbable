export interface User {
  uid: string;
  email: string;
  displayName?: string;
  isAdmin: boolean;
}

export interface FeatureRequest {
  id: string;
  title: string;
  description: string;
  authorId: string;
  authorEmail: string;
  votes: number;
  createdAt: string;
  updatedAt: string;
}

export interface Vote {
  id: string;
  userId: string;
  requestId: string;
  createdAt: string;
}

export interface CreateFeatureRequestDto {
  title: string;
  description: string;
}

export interface ApiError {
  detail: string;
}
