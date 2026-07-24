import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { FormGroup } from '@angular/forms';

import { ContactComponent } from './contact.component';

describe('ContactComponent', () => {
  it('persists a valid contact message and resets the form', async () => {
    await TestBed.configureTestingModule({
      imports: [ContactComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    const fixture = TestBed.createComponent(ContactComponent);
    const component = fixture.componentInstance as unknown as {
      form: FormGroup;
      send(): void;
    };
    component.form.setValue({ subject: 'Consulta', message: 'Necesito información.' });
    component.send();
    const request = TestBed.inject(HttpTestingController).expectOne(
      '/api/v1/contact-messages',
    );
    expect(request.request.method).toBe('POST');
    request.flush({});
    expect(component.form.value.subject).toBe('');
  });
});
