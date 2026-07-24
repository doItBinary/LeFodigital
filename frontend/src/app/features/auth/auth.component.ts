import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';

import { ApiErrorService } from '../../core/services/api-error.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';

@Component({
  selector: 'app-auth',
  imports: [ReactiveFormsModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);
  private readonly router = inject(Router);

  protected readonly registering = signal(false);
  protected readonly busy = signal(false);
  protected readonly loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });
  protected readonly registerForm = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    role: ['student' as 'student' | 'teacher', Validators.required],
    teacherInvitationCode: [''],
  });

  protected useDemo(role: 'teacher' | 'student'): void {
    const credentials =
      role === 'teacher'
        ? { email: 'prof@demo.com', password: 'prof123' }
        : { email: 'est@demo.com', password: 'est123' };
    this.registering.set(false);
    this.loginForm.setValue(credentials);
  }

  protected toggleContrast(): void {
    document.body.classList.toggle('high-contrast');
  }

  protected adjustFont(delta: number): void {
    const root = document.documentElement;
    const current = Number.parseFloat(getComputedStyle(root).fontSize) || 16;
    root.style.fontSize = `${Math.max(12, Math.min(20, current + delta))}px`;
  }

  protected login(): void {
    if (this.loginForm.invalid || this.busy()) {
      this.loginForm.markAllAsTouched();
      return;
    }
    this.busy.set(true);
    const { email, password } = this.loginForm.getRawValue();
    this.auth
      .login(email, password)
      .pipe(finalize(() => this.busy.set(false)))
      .subscribe({
        next: () => void this.router.navigate(['/activities']),
        error: (error) => this.toast.show(`❌ ${this.errors.message(error)}`),
      });
  }

  protected register(): void {
    if (this.registerForm.invalid || this.busy()) {
      this.registerForm.markAllAsTouched();
      return;
    }
    this.busy.set(true);
    this.auth
      .register(this.registerForm.getRawValue())
      .pipe(finalize(() => this.busy.set(false)))
      .subscribe({
        next: ({ message }) => {
          this.toast.show(`✅ ${message}`);
          this.registering.set(false);
          this.registerForm.reset({
            name: '',
            email: '',
            password: '',
            role: 'student',
            teacherInvitationCode: '',
          });
        },
        error: (error) => this.toast.show(`⚠️ ${this.errors.message(error)}`),
      });
  }
}
