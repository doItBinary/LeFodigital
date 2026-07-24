import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from './services/auth.service';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  const isAuthRequest = request.url.includes('/auth/');
  const token = auth.accessToken();
  const authenticatedRequest = token
    ? request.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : request;

  return next(authenticatedRequest).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status !== 401 || isAuthRequest) {
        return throwError(() => error);
      }
      return auth.refresh().pipe(
        switchMap((session) => {
          if (!session) {
            return throwError(() => error);
          }
          return next(
            request.clone({
              setHeaders: { Authorization: `Bearer ${session.accessToken}` },
            }),
          );
        }),
      );
    }),
  );
};
