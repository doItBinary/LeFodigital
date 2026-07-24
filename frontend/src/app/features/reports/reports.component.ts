import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';

import { StudentReport, TeacherReport } from '../../core/models/api.models';
import { ApiErrorService } from '../../core/services/api-error.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { ReportsService } from './reports.service';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportsComponent implements OnInit {
  private readonly api = inject(ReportsService);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);

  protected readonly auth = inject(AuthService);
  protected readonly studentReport = signal<StudentReport | null>(null);
  protected readonly teacherReport = signal<TeacherReport | null>(null);

  ngOnInit(): void {
    if (this.auth.isTeacher()) {
      this.api.teacher().subscribe({
        next: (report) => this.teacherReport.set(report),
        error: (error) => this.toast.show(this.errors.message(error)),
      });
    } else {
      this.api.student().subscribe({
        next: (report) => this.studentReport.set(report),
        error: (error) => this.toast.show(this.errors.message(error)),
      });
    }
  }

  protected async exportPdf(): Promise<void> {
    const [{ jsPDF }, autoTableModule] = await Promise.all([
      import('jspdf'),
      import('jspdf-autotable'),
    ]);
    const autoTable = autoTableModule.default;
    const report = this.studentReport();
    if (report) {
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text('LeFodigital — Reporte de progreso', 14, 18);
      doc.setFontSize(10);
      doc.text(`Estudiante: ${report.name} · ${report.email}`, 14, 26);
      autoTable(doc, {
        startY: 34,
        head: [['Puntos', 'Nivel', 'Completadas', 'Medallas']],
        body: [[
          report.progress.points,
          report.progress.level,
          `${report.progress.completedActivities}/${report.totalPublishedActivities}`,
          report.progress.medals.length,
        ]],
      });
      autoTable(doc, {
        startY: 58,
        head: [['Actividad', 'Puntos', 'Evidencia']],
        body: report.completed.map((activity) => [
          activity.title,
          activity.points,
          activity.myEvidence?.originalName ?? 'Sin evidencia',
        ]),
      });
      doc.save('reporte-progreso-lefodigital.pdf');
      return;
    }
    const teacher = this.teacherReport();
    if (!teacher) {
      return;
    }
    const doc = new jsPDF({ orientation: 'landscape' });
    doc.setFontSize(18);
    doc.text('LeFodigital — Reporte general', 14, 18);
    autoTable(doc, {
      startY: 28,
      head: [['Estudiante', 'Correo', 'Nivel', 'Puntos', 'Progreso', 'Medallas', 'Evidencias']],
      body: teacher.students.map((student) => [
        student.name,
        student.email,
        student.progress.level,
        student.progress.points,
        `${student.progressPercent}%`,
        student.progress.medals.length,
        student.evidenceCount,
      ]),
    });
    doc.save('reporte-general-lefodigital.pdf');
  }

  protected async exportExcel(): Promise<void> {
    const XLSX = await import('xlsx');
    const workbook = XLSX.utils.book_new();
    const report = this.studentReport();
    if (report) {
      const summary = XLSX.utils.json_to_sheet([
        {
          Estudiante: report.name,
          Correo: report.email,
          Puntos: report.progress.points,
          Nivel: report.progress.level,
          'Actividades completadas': report.progress.completedActivities,
          'Total actividades': report.totalPublishedActivities,
          Medallas: report.progress.medals.map((medal) => medal.name).join(', '),
        },
      ]);
      const activities = XLSX.utils.json_to_sheet(
        report.completed.map((activity) => ({
          Actividad: activity.title,
          Descripción: activity.description,
          Puntos: activity.points,
          Evidencia: activity.myEvidence?.originalName ?? 'Sin evidencia',
        })),
      );
      XLSX.utils.book_append_sheet(workbook, summary, 'Resumen');
      XLSX.utils.book_append_sheet(workbook, activities, 'Actividades');
      XLSX.writeFile(workbook, 'reporte-progreso-lefodigital.xlsx');
      return;
    }
    const teacher = this.teacherReport();
    if (!teacher) {
      return;
    }
    const sheet = XLSX.utils.json_to_sheet(
      teacher.students.map((student) => ({
        Nombre: student.name,
        Correo: student.email,
        Institución: student.institution,
        Nivel: student.progress.level,
        Puntos: student.progress.points,
        Completadas: student.progress.completedActivities,
        'Total actividades': student.totalPublishedActivities,
        'Progreso %': student.progressPercent,
        Medallas: student.progress.medals.map((medal) => medal.name).join(', '),
        Evidencias: student.evidenceCount,
      })),
    );
    XLSX.utils.book_append_sheet(workbook, sheet, 'Estudiantes');
    XLSX.writeFile(workbook, 'reporte-general-lefodigital.xlsx');
  }
}
