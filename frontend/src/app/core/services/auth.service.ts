import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { catchError, finalize, Observable, of, shareReplay, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AuthSession, UserProfile, UserRole } from '../models/api.models';

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
  teacherInvitationCode?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly token = signal<string | null>(null);
  private refreshRequest?: Observable<AuthSession | null>;

  readonly user = signal<UserProfile | null>(null);
  readonly initialized = signal(false);
  readonly isAuthenticated = computed(() => this.user() !== null);
  readonly isTeacher = computed(() => this.user()?.role === 'teacher');

  accessToken(): string | null {
    return this.token();
  }

  login(email: string, password: string): Observable<AuthSession> {
    return this.http
      .post<AuthSession>(
        `${environment.apiUrl}/auth/login`,
        { email, password },
        { withCredentials: true },
      )
      .pipe(tap((session) => this.applySession(session)));
  }

  register(payload: RegisterPayload): Observable<{ message: string; user: UserProfile }> {
    return this.http.post<{ message: string; user: UserProfile }>(
      `${environment.apiUrl}/auth/register`,
      payload,
    );
  }

  restore(): Observable<AuthSession | null> {
    return this.refresh().pipe(
      catchError(() => of(null)),
      finalize(() => this.initialized.set(true)),
    );
  }

  refresh(): Observable<AuthSession | null> {
    if (!this.refreshRequest) {
      this.refreshRequest = this.http
        .post<AuthSession>(
          `${environment.apiUrl}/auth/refresh`,
          {},
          { withCredentials: true },
        )
        .pipe(
          tap((session) => this.applySession(session)),
          catchError(() => {
            this.clearSession();
            return of(null);
          }),
          finalize(() => {
            this.refreshRequest = undefined;
          }),
          shareReplay(1),
        );
    }
    return this.refreshRequest;
  }

  logout(): Observable<void> {
    return this.http
      .post<void>(`${environment.apiUrl}/auth/logout`, {}, { withCredentials: true })
      .pipe(finalize(() => this.clearSession()));
  }

  updateUser(user: UserProfile): void {
    this.user.set(user);
  }

  private applySession(session: AuthSession): void {
    this.token.set(session.accessToken);
    this.user.set(session.user);
  }

  private clearSession(): void {
    this.token.set(null);
    this.user.set(null);
  }
}
