import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { ChatComponent } from './chat.component';
import { ChatService } from './chat.service';

describe('ChatComponent', () => {
  const send = vi.fn();

  beforeEach(async () => {
    send.mockReset();
    await TestBed.configureTestingModule({
      imports: [ChatComponent],
      providers: [{ provide: ChatService, useValue: { send } }],
    }).compileComponents();
  });

  it('opens and closes an accessible dialog', () => {
    const fixture = TestBed.createComponent(ChatComponent);
    fixture.detectChanges();
    (fixture.nativeElement.querySelector('.chat-fab') as HTMLButtonElement).click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="dialog"]')).toBeTruthy();
    (fixture.nativeElement.querySelector('.chat-close') as HTMLButtonElement).click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="dialog"]')).toBeNull();
  });

  it('adds user and assistant messages without persisting history', () => {
    send.mockReturnValue(of({ message: 'Respuesta educativa.' }));
    const fixture = TestBed.createComponent(ChatComponent);
    const component = fixture.componentInstance as unknown as {
      draft: string;
      send(): void;
      messages(): { role: string; content: string }[];
    };
    component.draft = '¿Cómo estudio mejor?';
    component.send();
    expect(send).toHaveBeenCalledOnce();
    expect(component.messages().at(-1)?.content).toBe('Respuesta educativa.');
  });

  it('shows a friendly error from the provider', () => {
    send.mockReturnValue(
      throwError(() => ({ error: { message: 'Servicio temporalmente no disponible.' } })),
    );
    const fixture = TestBed.createComponent(ChatComponent);
    const component = fixture.componentInstance as unknown as {
      draft: string;
      send(): void;
      messages(): { role: string; content: string }[];
    };
    component.draft = 'Hola';
    component.send();
    expect(component.messages().at(-1)?.content).toContain('LeFoBot no está disponible');
  });

  it('keeps no more than ten temporary messages', () => {
    send.mockReturnValue(of({ message: 'Respuesta.' }));
    const fixture = TestBed.createComponent(ChatComponent);
    const component = fixture.componentInstance as unknown as {
      draft: string;
      send(): void;
      messages(): { role: string; content: string }[];
    };
    for (let index = 0; index < 8; index += 1) {
      component.draft = `Pregunta ${index}`;
      component.send();
    }
    expect(component.messages()).toHaveLength(10);
    expect(component.messages().at(-1)?.content).toBe('Respuesta.');
  });
});
