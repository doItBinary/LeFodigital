import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { environment } from '../../../environments/environment';
import { ApiErrorService } from '../../core/services/api-error.service';
import { ToastService } from '../../core/services/toast.service';

@Component({
  selector: 'app-contact',
  imports: [ReactiveFormsModule],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContactComponent {
  private readonly http = inject(HttpClient);
  private readonly fb = inject(FormBuilder);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);

  protected readonly form = this.fb.nonNullable.group({
    subject: ['', [Validators.required, Validators.minLength(2)]],
    message: ['', [Validators.required, Validators.minLength(2)]],
  });

  protected send(): void {
    if (this.form.invalid) {
      return;
    }
    this.http
      .post(`${environment.apiUrl}/contact-messages`, this.form.getRawValue())
      .subscribe({
        next: () => {
          this.form.reset();
          this.toast.show('📨 Mensaje guardado correctamente.');
        },
        error: (error) => this.toast.show(this.errors.message(error)),
      });
  }
}
