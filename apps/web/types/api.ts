/**
 * Common API Types
 */

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface MessageResponse {
  message: string;
}
