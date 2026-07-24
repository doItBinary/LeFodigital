import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { finalize } from 'rxjs';

import {
  ActivitySummary,
  CourseSummary,
  EvidenceMetadata,
} from '../../core/models/api.models';
import { ApiErrorService } from '../../core/services/api-error.service';
import { AuthService } from '../../core/services/auth.service';
import { GamificationService } from '../../core/services/gamification.service';
import { ToastService } from '../../core/services/toast.service';
import { CoursesService } from '../courses/courses.service';
import { ActivitiesService } from './activities.service';

@Component({
  selector: 'app-activities',
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './activities.component.html',
  styleUrl: './activities.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivitiesComponent implements OnInit {
  private readonly activitiesApi = inject(ActivitiesService);
  private readonly coursesApi = inject(CoursesService);
  private readonly fb = inject(FormBuilder);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);
  private readonly route = inject(ActivatedRoute);
  private readonly gamification = inject(GamificationService);

  protected readonly auth = inject(AuthService);
  protected readonly activities = signal<ActivitySummary[]>([]);
  protected readonly courses = signal<CourseSummary[]>([]);
  protected readonly busy = signal(false);
  protected readonly showCreate = signal(false);
  protected readonly evidenceByActivity = signal<Record<string, EvidenceMetadata[]>>({});
  protected readonly selectedFiles = new Map<string, File>();
  protected readonly form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.minLength(2)]],
    description: [''],
    points: [10, [Validators.required, Validators.min(1)]],
    dueDate: [''],
    courseId: [''],
  });

  ngOnInit(): void {
    this.showCreate.set(this.route.snapshot.queryParamMap.get('create') === '1');
    this.load();
    if (this.auth.isTeacher()) {
      this.coursesApi.list().subscribe((courses) => this.courses.set(courses));
    }
  }

  protected load(): void {
    this.busy.set(true);
    this.activitiesApi
      .list()
      .pipe(finalize(() => this.busy.set(false)))
      .subscribe({
        next: (activities) => this.activities.set(activities),
        error: (error) => this.toast.show(this.errors.message(error)),
      });
  }

  protected create(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const data = this.form.getRawValue();
    this.activitiesApi
      .create({
        title: data.title,
        description: data.description,
        points: data.points,
        dueDate: data.dueDate || null,
        courseId: data.courseId || null,
      })
      .subscribe({
        next: () => {
          this.toast.show('✅ Actividad creada como borrador.');
          this.form.reset({ title: '', description: '', points: 10, dueDate: '', courseId: '' });
          this.showCreate.set(false);
          this.load();
        },
        error: (error) => this.toast.show(this.errors.message(error)),
      });
  }

  protected publish(activity: ActivitySummary): void {
    this.activitiesApi.publish(activity.id).subscribe({
      next: () => {
        this.toast.show('✅ Actividad asignada a todos los estudiantes.');
        this.load();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected remove(activity: ActivitySummary): void {
    if (!window.confirm(`¿Eliminar "${activity.title}" y revertir su progreso asociado?`)) {
      return;
    }
    this.activitiesApi.remove(activity.id).subscribe({
      next: () => {
        this.toast.show('Actividad eliminada.');
        this.load();
        this.gamification.load().subscribe();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected complete(activity: ActivitySummary): void {
    if (!window.confirm(`¿Marcar "${activity.title}" como completada y recibir ${activity.points} puntos?`)) {
      return;
    }
    this.activitiesApi.complete(activity.id).subscribe({
      next: ({ message }) => {
        this.toast.show(`🎉 ${message} +${activity.points} puntos`);
        this.load();
        this.gamification.load().subscribe();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected selectFile(activityId: string, event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) {
      this.selectedFiles.delete(activityId);
      return;
    }
    if (file.size > 1_048_576) {
      this.toast.show('⚠️ El archivo supera el límite de 1 MB.');
      (event.target as HTMLInputElement).value = '';
      return;
    }
    this.selectedFiles.set(activityId, file);
  }

  protected upload(activityId: string): void {
    const file = this.selectedFiles.get(activityId);
    if (!file) {
      return;
    }
    this.activitiesApi.upload(activityId, file).subscribe({
      next: () => {
        this.selectedFiles.delete(activityId);
        this.toast.show('📎 Evidencia guardada.');
        this.load();
        this.gamification.load().subscribe();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected toggleEvidences(activityId: string): void {
    if (this.evidenceByActivity()[activityId]) {
      const current = { ...this.evidenceByActivity() };
      delete current[activityId];
      this.evidenceByActivity.set(current);
      return;
    }
    this.activitiesApi.evidences(activityId).subscribe({
      next: (evidences) =>
        this.evidenceByActivity.update((current) => ({ ...current, [activityId]: evidences })),
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected download(evidence: EvidenceMetadata): void {
    this.activitiesApi.download(evidence.id).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = evidence.originalName;
        link.click();
        URL.revokeObjectURL(url);
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }
}
