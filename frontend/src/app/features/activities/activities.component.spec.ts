import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { FormGroup } from '@angular/forms';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { ActivitySummary, EvidenceMetadata } from '../../core/models/api.models';
import { AuthService } from '../../core/services/auth.service';
import { GamificationService } from '../../core/services/gamification.service';
import { CoursesService } from '../courses/courses.service';
import { ActivitiesComponent } from './activities.component';
import { ActivitiesService } from './activities.service';

const activity: ActivitySummary = {
  id: 'activity-1',
  title: 'Actividad digital',
  description: 'Descripción',
  points: 50,
  dueDate: null,
  status: 'published',
  courseId: null,
  courseName: null,
  authorName: 'Profesor Demo',
  createdAt: '2026-07-24T00:00:00Z',
  publishedAt: '2026-07-24T00:00:00Z',
  completed: false,
  completionCount: 0,
  evidenceCount: 0,
  myEvidence: null,
};

const evidence: EvidenceMetadata = {
  id: 'evidence-1',
  activityId: activity.id,
  studentId: 'student-1',
  studentName: 'Estudiante Demo',
  originalName: 'evidencia.pdf',
  contentType: 'application/pdf',
  sizeBytes: 10,
  uploadedAt: '2026-07-24T00:00:00Z',
};

describe('ActivitiesComponent', () => {
  it('covers the teacher and student activity actions', async () => {
    const api = {
      list: vi.fn().mockReturnValue(of([activity])),
      create: vi.fn().mockReturnValue(of(activity)),
      publish: vi.fn().mockReturnValue(of(activity)),
      remove: vi.fn().mockReturnValue(of(undefined)),
      complete: vi.fn().mockReturnValue(of({ message: 'Actividad completada.', activity })),
      upload: vi.fn().mockReturnValue(of(evidence)),
      evidences: vi.fn().mockReturnValue(of([evidence])),
      download: vi.fn().mockReturnValue(of(new Blob(['pdf']))),
    };
    const loadProgress = vi.fn().mockReturnValue(of({}));
    await TestBed.configureTestingModule({
      imports: [ActivitiesComponent],
      providers: [
        { provide: ActivitiesService, useValue: api },
        { provide: CoursesService, useValue: { list: () => of([]) } },
        { provide: AuthService, useValue: { isTeacher: signal(true) } },
        { provide: GamificationService, useValue: { load: loadProgress } },
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { queryParamMap: convertToParamMap({ create: '1' }) } },
        },
      ],
    }).compileComponents();
    const component = TestBed.createComponent(ActivitiesComponent)
      .componentInstance as unknown as {
      form: FormGroup;
      showCreate(): boolean;
      selectedFiles: Map<string, File>;
      evidenceByActivity(): Record<string, EvidenceMetadata[]>;
      ngOnInit(): void;
      create(): void;
      publish(item: ActivitySummary): void;
      remove(item: ActivitySummary): void;
      complete(item: ActivitySummary): void;
      selectFile(id: string, event: Event): void;
      upload(id: string): void;
      toggleEvidences(id: string): void;
      download(item: EvidenceMetadata): void;
    };
    component.ngOnInit();
    expect(component.showCreate()).toBe(true);

    component.form.setValue({
      title: 'Nueva actividad',
      description: 'Descripción',
      points: 25,
      dueDate: '',
      courseId: '',
    });
    component.create();
    component.publish(activity);

    vi.spyOn(window, 'confirm').mockReturnValue(true);
    component.complete(activity);
    component.remove(activity);

    const file = new File(['pdf'], 'evidencia.pdf', { type: 'application/pdf' });
    component.selectFile(
      activity.id,
      { target: { files: [file], value: '' } } as unknown as Event,
    );
    expect(component.selectedFiles.get(activity.id)).toBe(file);
    component.upload(activity.id);

    component.toggleEvidences(activity.id);
    expect(component.evidenceByActivity()[activity.id]).toEqual([evidence]);
    component.toggleEvidences(activity.id);
    expect(component.evidenceByActivity()[activity.id]).toBeUndefined();

    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test');
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    component.download(evidence);

    expect(api.create).toHaveBeenCalledOnce();
    expect(api.publish).toHaveBeenCalledWith(activity.id);
    expect(api.complete).toHaveBeenCalledWith(activity.id);
    expect(api.remove).toHaveBeenCalledWith(activity.id);
    expect(api.upload).toHaveBeenCalledWith(activity.id, file);
    expect(loadProgress).toHaveBeenCalledTimes(3);
  });
});
