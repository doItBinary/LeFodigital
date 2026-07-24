import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { StudentReport, TeacherReport } from '../../core/models/api.models';
import { AuthService } from '../../core/services/auth.service';
import { ReportsComponent } from './reports.component';
import { ReportsService } from './reports.service';

const exports = vi.hoisted(() => ({
  autoTable: vi.fn(),
  save: vi.fn(),
  writeFile: vi.fn(),
  bookAppendSheet: vi.fn(),
  bookNew: vi.fn(() => ({})),
  jsonToSheet: vi.fn(() => ({})),
}));

vi.mock('jspdf', () => ({
  jsPDF: class {
    setFontSize(): void {}
    text(): void {}
    save(name: string): void {
      exports.save(name);
    }
  },
}));
vi.mock('jspdf-autotable', () => ({ default: exports.autoTable }));
vi.mock('xlsx', () => ({
  utils: {
    book_new: exports.bookNew,
    json_to_sheet: exports.jsonToSheet,
    book_append_sheet: exports.bookAppendSheet,
  },
  writeFile: exports.writeFile,
}));

const progress = {
  points: 50,
  level: 1,
  completedActivities: 1,
  medals: [],
  pointsInLevel: 50,
};
const completed = {
  id: 'activity-1',
  title: 'Actividad',
  description: 'Descripción',
  points: 50,
  dueDate: null,
  status: 'published' as const,
  courseId: null,
  courseName: null,
  authorName: 'Profesor',
  createdAt: '2026-07-24T00:00:00Z',
  publishedAt: '2026-07-24T00:00:00Z',
  completed: true,
  completionCount: 1,
  evidenceCount: 0,
  myEvidence: null,
};
const studentReport: StudentReport = {
  studentId: 'student-1',
  name: 'Estudiante Demo',
  email: 'est@demo.com',
  institution: '',
  progress,
  totalPublishedActivities: 1,
  completed: [completed],
};
const teacherReport: TeacherReport = {
  students: [
    {
      studentId: 'student-1',
      name: 'Estudiante Demo',
      email: 'est@demo.com',
      institution: '',
      progress,
      totalPublishedActivities: 1,
      progressPercent: 100,
      evidenceCount: 0,
    },
  ],
  totalStudents: 1,
  totalPublishedActivities: 1,
  averagePoints: 50,
  averageLevel: 1,
  totalMedals: 0,
};

describe('ReportsComponent', () => {
  beforeEach(() => {
    exports.autoTable.mockClear();
    exports.save.mockClear();
    exports.writeFile.mockClear();
  });

  async function createComponent(isTeacher: boolean) {
    await TestBed.configureTestingModule({
      imports: [ReportsComponent],
      providers: [
        { provide: AuthService, useValue: { isTeacher: signal(isTeacher) } },
        {
          provide: ReportsService,
          useValue: {
            student: () => of(studentReport),
            teacher: () => of(teacherReport),
          },
        },
      ],
    }).compileComponents();
    return TestBed.createComponent(ReportsComponent)
      .componentInstance as unknown as {
      ngOnInit(): void;
      exportPdf(): Promise<void>;
      exportExcel(): Promise<void>;
    };
  }

  it('loads and exports the authorized student report', async () => {
    const component = await createComponent(false);
    component.ngOnInit();
    await component.exportPdf();
    await component.exportExcel();
    expect(exports.autoTable).toHaveBeenCalled();
    expect(exports.save).toHaveBeenCalledWith('reporte-progreso-lefodigital.pdf');
    expect(exports.writeFile).toHaveBeenCalledWith(
      expect.anything(),
      'reporte-progreso-lefodigital.xlsx',
    );
  });

  it('loads and exports the general teacher report', async () => {
    const component = await createComponent(true);
    component.ngOnInit();
    await component.exportPdf();
    await component.exportExcel();
    expect(exports.save).toHaveBeenCalledWith('reporte-general-lefodigital.pdf');
    expect(exports.writeFile).toHaveBeenCalledWith(
      expect.anything(),
      'reporte-general-lefodigital.xlsx',
    );
  });
});
