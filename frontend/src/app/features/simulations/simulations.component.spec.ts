import { TestBed } from '@angular/core/testing';

import { SimulationsComponent } from './simulations.component';

describe('SimulationsComponent', () => {
  it('renders external simulations as links', async () => {
    await TestBed.configureTestingModule({ imports: [SimulationsComponent] }).compileComponents();
    const fixture = TestBed.createComponent(SimulationsComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Simulaciones');
    expect(fixture.nativeElement.querySelectorAll('a').length).toBeGreaterThan(0);
  });
});
