import { TestBed } from '@angular/core/testing';

import { LibraryComponent } from './library.component';

describe('LibraryComponent', () => {
  it('renders the educational resource catalogue', async () => {
    await TestBed.configureTestingModule({ imports: [LibraryComponent] }).compileComponents();
    const fixture = TestBed.createComponent(LibraryComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Biblioteca');
    expect(fixture.nativeElement.querySelectorAll('a').length).toBeGreaterThan(0);
  });
});
