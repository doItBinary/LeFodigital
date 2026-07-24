import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AuthSession } from '../models/api.models';
import { AuthService } from './auth.service';

const session: AuthSession = {
  accessToken: 'access-token',
  tokenType: 'bearer',
  expiresIn: 900,
  user: {
    id: 'user-1',
    name: 'Estudiante Demo',
    email: 'est@demo.com',
    role: 'student',
    institution: '',
    createdAt: '2026-07-24T00:00:00Z',
  },
};

describe('AuthService', () => {
  let service: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('logs in and keeps the access token only in memory', () => {
    service.login('est@demo.com', 'est123').subscribe();
    const request = http.expectOne('/api/v1/auth/login');
    expect(request.request.withCredentials).toBe(true);
    request.flush(session);
    expect(service.user()?.email).toBe('est@demo.com');
    expect(service.accessToken()).toBe('access-token');
    expect(localStorage.length).toBe(0);
  });

  it('registers a teacher with the invitation code', () => {
    service
      .register({
        name: 'Docente',
        email: 'teacher@example.com',
        password: 'password123',
        role: 'teacher',
        teacherInvitationCode: 'CODE',
      })
      .subscribe((response) => expect(response.message).toBe('Cuenta creada.'));
    const request = http.expectOne('/api/v1/auth/register');
    expect(request.request.body.teacherInvitationCode).toBe('CODE');
    request.flush({ message: 'Cuenta creada.', user: session.user });
  });

  it('restores, refreshes and clears a session on logout', () => {
    service.restore().subscribe((restored) => expect(restored?.accessToken).toBe('access-token'));
    http.expectOne('/api/v1/auth/refresh').flush(session);
    expect(service.initialized()).toBe(true);

    service.logout().subscribe();
    http.expectOne('/api/v1/auth/logout').flush(null);
    expect(service.user()).toBeNull();
    expect(service.accessToken()).toBeNull();
  });

  it('handles a missing refresh cookie without exposing an error', () => {
    service.restore().subscribe((restored) => expect(restored).toBeNull());
    http.expectOne('/api/v1/auth/refresh').flush(
      { code: 'invalid_refresh_token', message: 'Sesión vencida.' },
      { status: 401, statusText: 'Unauthorized' },
    );
    expect(service.initialized()).toBe(true);
  });

  it('updates the current user after profile changes', () => {
    service.login('est@demo.com', 'est123').subscribe();
    http.expectOne('/api/v1/auth/login').flush(session);
    service.updateUser({ ...session.user, institution: 'I.E. Rural' });
    expect(service.user()?.institution).toBe('I.E. Rural');
    expect(service.isTeacher()).toBe(false);
    expect(service.isAuthenticated()).toBe(true);
  });
});
