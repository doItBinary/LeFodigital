import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { environment } from '../../../environments/environment';
import { UserProfile } from '../../core/models/api.models';
import { ApiErrorService } from '../../core/services/api-error.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';

@Component({
  selector: 'app-profile',
  imports: [ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfileComponent {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);
  private readonly current = this.auth.user();

  protected readonly form = this.fb.nonNullable.group({
    name: [this.current?.name ?? '', [Validators.required, Validators.minLength(2)]],
    email: [{ value: this.current?.email ?? '', disabled: true }],
    institution: [this.current?.institution ?? ''],
  });

  protected save(): void {
    if (this.form.invalid) {
      return;
    }
    const data = this.form.getRawValue();
    this.http
      .patch<UserProfile>(`${environment.apiUrl}/users/me`, {
        name: data.name,
        institution: data.institution,
      })
      .subscribe({
        next: (user) => {
          this.auth.updateUser(user);
          this.toast.show('✅ Perfil actualizado.');
        },
        error: (error) => this.toast.show(this.errors.message(error)),
      });
  }
}
