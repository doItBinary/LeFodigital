import { TestBed } from '@angular/core/testing';

import { ToastService } from '../../core/services/toast.service';
import { ToastComponent } from './toast.component';

describe('ToastComponent', () => {
  it('announces a visible notification', async () => {
    await TestBed.configureTestingModule({ imports: [ToastComponent] }).compileComponents();
    const fixture = TestBed.createComponent(ToastComponent);
    TestBed.inject(ToastService).show('Cambios guardados');
    fixture.detectChanges();
    const alert = fixture.nativeElement.querySelector('[role="status"]');
    expect(alert?.textContent).toContain('Cambios guardados');
  });
});
