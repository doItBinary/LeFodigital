import { TestBed } from '@angular/core/testing';
import { FormGroup } from '@angular/forms';
import { provideRouter, Router } from '@angular/router';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { AuthService, RegisterPayload } from '../../core/services/auth.service';
import { AuthComponent } from './auth.component';

describe('AuthComponent', () => {
  const login = vi.fn();
  const register = vi.fn();

  beforeEach(async () => {
    login.mockReset().mockReturnValue(of({}));
    register.mockReset().mockReturnValue(
      of({ message: 'Cuenta creada.', user: {} }),
    );
    await TestBed.configureTestingModule({
      imports: [AuthComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: { login, register } },
      ],
    }).compileComponents();
  });

  it('submits a valid login and navigates to activities', () => {
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    const component = TestBed.createComponent(AuthComponent)
      .componentInstance as unknown as {
      loginForm: FormGroup;
      login(): void;
    };
    component.loginForm.setValue({ email: 'est@demo.com', password: 'est123' });
    component.login();
    expect(login).toHaveBeenCalledWith('est@demo.com', 'est123');
    expect(navigate).toHaveBeenCalledWith(['/activities']);
  });

  it('includes the invitation code in teacher registration', () => {
    const component = TestBed.createComponent(AuthComponent)
      .componentInstance as unknown as {
      registerForm: FormGroup;
      register(): void;
    };
    const payload: RegisterPayload = {
      name: 'Docente Rural',
      email: 'teacher@example.com',
      password: 'password123',
      role: 'teacher',
      teacherInvitationCode: 'DOCENTE-TEST',
    };
    component.registerForm.setValue(payload);
    component.register();
    expect(register).toHaveBeenCalledWith(payload);
  });
});
