import { ref } from 'vue';
import type { ApiError } from '@/types';

export function useErrorHandler() {
  const error = ref<string>('');
  const isError = ref<boolean>(false);

  function setError(err: unknown): void {
    isError.value = true;
    
    if (err instanceof Error) {
      error.value = err.message;
    } else if (typeof err === 'string') {
      error.value = err;
    } else if (err && typeof err === 'object' && 'error' in err) {
      error.value = (err as ApiError).error;
    } else {
      error.value = 'An unexpected error occurred';
    }
  }

  function clearError(): void {
    error.value = '';
    isError.value = false;
  }

  async function handleAsync<T>(
    promise: Promise<T>,
    errorMessage?: string
  ): Promise<T | null> {
    try {
      clearError();
      return await promise;
    } catch (err) {
      setError(errorMessage || err);
      return null;
    }
  }

  return {
    error,
    isError,
    setError,
    clearError,
    handleAsync,
  };
}