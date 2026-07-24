import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { GamificationProgress } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class GamificationService {
  private readonly http = inject(HttpClient);
  readonly progress = signal<GamificationProgress | null>(null);

  load() {
    return this.http
      .get<GamificationProgress>(`${environment.apiUrl}/gamification/me`)
      .pipe(tap((progress) => this.progress.set(progress)));
  }
}
