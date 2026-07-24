import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';
import { StudentReport, TeacherReport } from '../../core/models/api.models';

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private readonly http = inject(HttpClient);

  student() {
    return this.http.get<StudentReport>(`${environment.apiUrl}/reports/student/me`);
  }

  teacher() {
    return this.http.get<TeacherReport>(`${environment.apiUrl}/reports/teacher`);
  }
}
