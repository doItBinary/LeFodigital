import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';
import { PostSummary } from '../../core/models/api.models';

@Injectable({ providedIn: 'root' })
export class BlogService {
  private readonly http = inject(HttpClient);

  list() {
    return this.http.get<PostSummary[]>(`${environment.apiUrl}/posts`);
  }

  create(title: string, content: string) {
    return this.http.post<PostSummary>(`${environment.apiUrl}/posts`, { title, content });
  }

  comment(postId: string, content: string) {
    return this.http.post<PostSummary>(`${environment.apiUrl}/posts/${postId}/comments`, {
      content,
    });
  }
}
