import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';
import { ChatMessage } from '../../core/models/api.models';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);

  send(messages: ChatMessage[]) {
    return this.http.post<{ message: string }>(`${environment.apiUrl}/chat/messages`, {
      messages: messages.slice(-10),
    });
  }
}
