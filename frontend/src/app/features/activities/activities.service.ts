import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';
import { ActivitySummary, EvidenceMetadata } from '../../core/models/api.models';

export interface CreateActivityPayload {
  title: string;
  description: string;
  points: number;
  dueDate: string | null;
  courseId: string | null;
}

@Injectable({ providedIn: 'root' })
export class ActivitiesService {
  private readonly http = inject(HttpClient);

  list() {
    return this.http.get<ActivitySummary[]>(`${environment.apiUrl}/activities`);
  }

  create(payload: CreateActivityPayload) {
    return this.http.post<ActivitySummary>(`${environment.apiUrl}/activities`, payload);
  }

  publish(activityId: string) {
    return this.http.post<ActivitySummary>(
      `${environment.apiUrl}/activities/${activityId}/publish`,
      {},
    );
  }

  complete(activityId: string) {
    return this.http.post<{ message: string; activity: ActivitySummary }>(
      `${environment.apiUrl}/activities/${activityId}/complete`,
      {},
    );
  }

  remove(activityId: string) {
    return this.http.delete<void>(`${environment.apiUrl}/activities/${activityId}`);
  }

  upload(activityId: string, file: File) {
    const body = new FormData();
    body.append('file', file);
    return this.http.post<EvidenceMetadata>(
      `${environment.apiUrl}/activities/${activityId}/evidence`,
      body,
    );
  }

  evidences(activityId: string) {
    return this.http.get<EvidenceMetadata[]>(
      `${environment.apiUrl}/activities/${activityId}/evidences`,
    );
  }

  download(evidenceId: string) {
    return this.http.get(`${environment.apiUrl}/evidences/${evidenceId}/download`, {
      responseType: 'blob',
    });
  }
}
