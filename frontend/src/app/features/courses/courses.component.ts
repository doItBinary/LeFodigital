import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import { CourseSummary } from '../../core/models/api.models';
import { ApiErrorService } from '../../core/services/api-error.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { CoursesService } from './courses.service';

@Component({
  selector: 'app-courses',
  imports: [ReactiveFormsModule],
  templateUrl: './courses.component.html',
  styleUrl: './courses.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CoursesComponent implements OnInit {
  private readonly api = inject(CoursesService);
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);

  protected readonly auth = inject(AuthService);
  protected readonly courses = signal<CourseSummary[]>([]);
  protected readonly showCreate = signal(false);
  protected readonly form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: [''],
  });

  ngOnInit(): void {
    this.showCreate.set(this.route.snapshot.queryParamMap.get('create') === '1');
    this.load();
  }

  protected load(): void {
    this.api.list().subscribe({
      next: (courses) => this.courses.set(courses),
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected create(): void {
    if (this.form.invalid) {
      return;
    }
    const data = this.form.getRawValue();
    this.api.create(data.name, data.description).subscribe({
      next: () => {
        this.toast.show('✅ Curso creado.');
        this.form.reset();
        this.showCreate.set(false);
        this.load();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }
}
