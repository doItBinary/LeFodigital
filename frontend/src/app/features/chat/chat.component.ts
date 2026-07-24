import { ChangeDetectionStrategy, Component, ElementRef, inject, signal, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { ChatMessage } from '../../core/models/api.models';
import { ApiErrorService } from '../../core/services/api-error.service';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatComponent {
  private readonly chat = inject(ChatService);
  private readonly errors = inject(ApiErrorService);
  private readonly inputElement = viewChild<ElementRef<HTMLInputElement>>('chatInput');

  protected readonly open = signal(false);
  protected readonly thinking = signal(false);
  protected readonly messages = signal<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        '¡Hola! ✦ Soy LeFoBot, tu asistente educativo. Pregúntame sobre temas académicos, estrategias de estudio o el uso de la plataforma.',
    },
  ]);
  protected draft = '';

  protected toggle(): void {
    this.open.update((value) => !value);
    if (this.open()) {
      setTimeout(() => this.inputElement()?.nativeElement.focus());
    }
  }

  protected close(): void {
    this.open.set(false);
  }

  protected send(): void {
    const content = this.draft.trim();
    if (!content || this.thinking()) {
      return;
    }
    this.draft = '';
    const history = [
      ...this.messages(),
      { role: 'user', content } satisfies ChatMessage,
    ].slice(-10);
    this.messages.set(history);
    this.thinking.set(true);
    this.chat
      .send(history)
      .pipe(finalize(() => this.thinking.set(false)))
      .subscribe({
        next: ({ message }) =>
          this.messages.update((items) =>
            [...items, { role: 'assistant', content: message } satisfies ChatMessage].slice(-10),
          ),
        error: (error) =>
          this.messages.update((items) =>
            [
              ...items,
              {
                role: 'assistant',
                content: this.errors.message(
                  error,
                  'LeFoBot no está disponible en este momento. Intenta más tarde.',
                ),
              } satisfies ChatMessage,
            ].slice(-10),
          ),
      });
  }
}
