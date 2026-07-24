import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ToastService {
  readonly message = signal('');
  private timeout?: ReturnType<typeof setTimeout>;

  show(message: string): void {
    this.message.set(message);
    clearTimeout(this.timeout);
    this.timeout = setTimeout(() => this.message.set(''), 3200);
  }
}
