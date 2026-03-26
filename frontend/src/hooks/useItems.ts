import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { Item } from '../types';

const fetchItems = async (): Promise<Item[]> => {
  const { data } = await apiClient.get('/items');
  return data;
};

export const useItems = () => {
  return useQuery({
    queryKey: ['items'],
    queryFn: fetchItems,
  });
};
