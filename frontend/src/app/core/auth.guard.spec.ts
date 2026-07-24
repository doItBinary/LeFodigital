import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router, UrlTree } from '@angular/router';

import { authGuard } from './auth.guard';
import { AuthService } from './services/auth.service';

describe('authGuard', () => {
  const authenticated = signal(false);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: { isAuthenticated: authenticated } },
      ],
    });
  });

  it('redirects anonymous users to auth', () => {
    authenticated.set(false);
    const result = TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));
    expect(result instanceof UrlTree).toBe(true);
    expect(TestBed.inject(Router).serializeUrl(result as UrlTree)).toBe('/auth');
  });

  it('allows authenticated users', () => {
    authenticated.set(true);
    expect(TestBed.runInInjectionContext(() => authGuard({} as never, {} as never))).toBe(true);
  });
});
