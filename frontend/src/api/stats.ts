import apiClient from './client';
import type { StatsOverview, EditFrequencyItem, TimelineData } from '../types';

export const fetchStatsOverview = async (): Promise<StatsOverview> => {
  const response = await apiClient.get<StatsOverview>('/stats');
  return response.data;
};

export const fetchEditFrequency = async (): Promise<EditFrequencyItem[]> => {
  const response = await apiClient.get<EditFrequencyItem[]>('/stats/edit-frequency');
  return response.data;
};

export const fetchTimeline = async (days = 30): Promise<TimelineData> => {
  const response = await apiClient.get<TimelineData>('/stats/timeline', {
    params: { days },
  });
  return response.data;
};
