import axios from 'axios';
import { Business } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const searchBusiness = async (businessName: string): Promise<Business> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/search/${encodeURIComponent(businessName)}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch business details');
  }
};

export const getBusinessById = async (id: number): Promise<Business> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/business/${id}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch business details');
  }
}; 