import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { Comment } from '../types';

const fetchItemComments = async (itemId: number): Promise<Comment[]> => {
  const { data } = await apiClient.get(`/items/${itemId}/comments`);
  return data;
};

export const useComments = (itemId: number | null) => {
  return useQuery({
    queryKey: ['comments', itemId],
    queryFn: () => fetchItemComments(itemId as number),
    enabled: !!itemId, // Only run the query if itemId is not null
  });
};

interface AddCommentPayload {
  itemId: number;
  content: string;
  userId?: number;
}

const postComment = async ({ itemId, content, userId = 1 }: AddCommentPayload) => {
  const { data } = await apiClient.post(`/items/${itemId}/comments`, {
    content,
    user_id: userId,
  });
  return data;
};

export const useAddComment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: postComment,
    onSuccess: (_, variables) => {
      // Invalidate the comments query for this specific item so it refetches instantly!
      queryClient.invalidateQueries({ queryKey: ['comments', variables.itemId] });
    },
  });
};
