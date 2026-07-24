import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { ApiErrorService } from './api-error.service';
import { ToastService } from './toast.service';

describe('Utility services', () => {
  it('extracts Spanish API messages and uses a fallback', () => {
    const service = TestBed.inject(ApiErrorService);
    const error = new HttpErrorResponse({
      status: 400,
      error: { code: 'invalid', message: 'Dato inválido.' },
    });
    expect(service.message(error)).toBe('Dato inválido.');
    expect(service.message(new Error('unknown'), 'Error controlado.')).toBe('Error controlado.');
  });

  it('publishes and clears toast messages', () => {
    vi.useFakeTimers();
    const service = TestBed.inject(ToastService);
    service.show('Guardado');
    expect(service.message()).toBe('Guardado');
    vi.advanceTimersByTime(3200);
    expect(service.message()).toBe('');
    vi.useRealTimers();
  });
});
