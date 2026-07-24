import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';
import { CourseSummary } from '../../core/models/api.models';

@Injectable({ providedIn: 'root' })
export class CoursesService {
  private readonly http = inject(HttpClient);

  list() {
    return this.http.get<CourseSummary[]>(`${environment.apiUrl}/courses`);
  }

  create(name: string, description: string) {
    return this.http.post<CourseSummary>(`${environment.apiUrl}/courses`, { name, description });
  }
}
