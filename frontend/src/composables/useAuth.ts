// System Utils
import { ref } from 'vue';

// Installed Utils
import type { AxiosRequestConfig } from 'axios';
import DOMPurify from 'dompurify';

// App Utils
import type { BaseUser, BaseUserEmail } from '@/interfaces/user';
import type ApiResponse from '@/interfaces/apiResponse';
import axios, { type AxiosResponse } from '@/axios';

export const useAuth = () => {
  const successMessage = ref('');
  const errorMessage = ref('');
  const isLoading = ref<boolean>(false);

  const authRequest = async <T = null>(
    url: string,
    user: BaseUser | BaseUserEmail,
    config?: AxiosRequestConfig,
  ): Promise<ApiResponse<T>> => {
    isLoading.value = true;
    successMessage.value = errorMessage.value = '';

    try {
      const response: AxiosResponse<ApiResponse<T>> = await axios.post(
        url,
        user,
        config,
      );

      if (response.data.success) {
        successMessage.value = DOMPurify.sanitize(response.data.message);
      } else {
        errorMessage.value = DOMPurify.sanitize(response.data.message);
      }

      return response.data;
    } catch (error) {
      errorMessage.value =
        error instanceof Error ? error.message : 'An error has occurred.';
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  return { authRequest, successMessage, errorMessage, isLoading };
};
