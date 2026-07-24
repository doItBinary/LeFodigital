import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { ApiError } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class ApiErrorService {
  message(error: unknown, fallback = 'No fue posible completar la operación.'): string {
    if (error instanceof HttpErrorResponse) {
      const apiError = error.error as Partial<ApiError> | undefined;
      return apiError?.message || fallback;
    }
    return fallback;
  }
}
