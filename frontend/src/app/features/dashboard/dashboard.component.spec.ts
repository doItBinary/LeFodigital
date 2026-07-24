import { computed, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../core/services/auth.service';
import { GamificationService } from '../../core/services/gamification.service';
import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  it('loads progress, applies accessibility controls and logs out', async () => {
    const user = signal({
      id: 'teacher-1',
      name: 'Profesor Demo',
      email: 'prof@demo.com',
      role: 'teacher' as const,
      institution: '',
      createdAt: '2026-07-24T00:00:00Z',
    });
    const load = vi.fn().mockReturnValue(of({}));
    const logout = vi.fn().mockReturnValue(of(undefined));
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: { user, isTeacher: computed(() => true), logout },
        },
        {
          provide: GamificationService,
          useValue: { load, progress: signal(null) },
        },
      ],
    }).compileComponents();
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    const component = TestBed.createComponent(DashboardComponent)
      .componentInstance as unknown as {
      ngOnInit(): void;
      toggleContrast(): void;
      adjustFont(delta: number): void;
      logout(): void;
    };
    component.ngOnInit();
    component.toggleContrast();
    component.adjustFont(1);
    component.logout();
    expect(load).toHaveBeenCalledOnce();
    expect(document.body.classList.contains('high-contrast')).toBe(true);
    expect(logout).toHaveBeenCalledOnce();
    expect(navigate).toHaveBeenCalledWith(['/auth']);
    document.body.classList.remove('high-contrast');
    document.documentElement.style.fontSize = '';
  });
});
