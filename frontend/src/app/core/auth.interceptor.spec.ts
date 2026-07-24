import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { authInterceptor } from './auth.interceptor';
import { AuthSession } from './models/api.models';
import { AuthService } from './services/auth.service';

const makeSession = (token: string): AuthSession => ({
  accessToken: token,
  tokenType: 'bearer',
  expiresIn: 900,
  user: {
    id: 'user-1',
    name: 'Usuario',
    email: 'user@example.com',
    role: 'student',
    institution: '',
    createdAt: '2026-07-24T00:00:00Z',
  },
});

describe('authInterceptor', () => {
  let client: HttpClient;
  let controller: HttpTestingController;
  let auth: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    client = TestBed.inject(HttpClient);
    controller = TestBed.inject(HttpTestingController);
    auth = TestBed.inject(AuthService);
  });

  afterEach(() => controller.verify());

  function login(): void {
    auth.login('user@example.com', 'password').subscribe();
    controller.expectOne('/api/v1/auth/login').flush(makeSession('old-token'));
  }

  it('adds the in-memory access token to protected requests', () => {
    login();
    client.get('/api/v1/users/me').subscribe();
    const request = controller.expectOne('/api/v1/users/me');
    expect(request.request.headers.get('Authorization')).toBe('Bearer old-token');
    request.flush({});
  });

  it('rotates the session and retries once after a 401', () => {
    login();
    client.get('/api/v1/users/me').subscribe();
    const first = controller.expectOne('/api/v1/users/me');
    first.flush({}, { status: 401, statusText: 'Unauthorized' });
    controller.expectOne('/api/v1/auth/refresh').flush(makeSession('new-token'));
    const retry = controller.expectOne('/api/v1/users/me');
    expect(retry.request.headers.get('Authorization')).toBe('Bearer new-token');
    retry.flush({});
  });

  it('shares one refresh request between concurrent 401 responses', () => {
    login();
    client.get('/api/v1/users/me').subscribe();
    client.get('/api/v1/activities').subscribe();

    controller
      .expectOne('/api/v1/users/me')
      .flush({}, { status: 401, statusText: 'Unauthorized' });
    controller
      .expectOne('/api/v1/activities')
      .flush({}, { status: 401, statusText: 'Unauthorized' });

    controller.expectOne('/api/v1/auth/refresh').flush(makeSession('shared-token'));

    const retries = controller.match(
      (request) =>
        request.url === '/api/v1/users/me' || request.url === '/api/v1/activities',
    );
    expect(retries).toHaveLength(2);
    for (const retry of retries) {
      expect(retry.request.headers.get('Authorization')).toBe('Bearer shared-token');
      retry.flush({});
    }
  });
});
