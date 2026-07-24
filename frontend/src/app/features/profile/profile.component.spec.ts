import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { FormGroup } from '@angular/forms';
import { vi } from 'vitest';

import { UserProfile } from '../../core/models/api.models';
import { AuthService } from '../../core/services/auth.service';
import { ProfileComponent } from './profile.component';

const profile: UserProfile = {
  id: 'student-1',
  name: 'Estudiante Demo',
  email: 'est@demo.com',
  role: 'student',
  institution: '',
  createdAt: '2026-07-24T00:00:00Z',
};

describe('ProfileComponent', () => {
  it('updates the editable profile through the API', async () => {
    const updateUser = vi.fn();
    await TestBed.configureTestingModule({
      imports: [ProfileComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { user: signal(profile), updateUser } },
      ],
    }).compileComponents();
    const fixture = TestBed.createComponent(ProfileComponent);
    const component = fixture.componentInstance as unknown as {
      form: FormGroup;
      save(): void;
    };
    component.form.controls['name'].setValue('Nombre Actualizado');
    component.form.controls['institution'].setValue('I.E. Rural');
    component.save();
    const request = TestBed.inject(HttpTestingController).expectOne('/api/v1/users/me');
    expect(request.request.method).toBe('PATCH');
    request.flush({ ...profile, name: 'Nombre Actualizado', institution: 'I.E. Rural' });
    expect(updateUser).toHaveBeenCalledOnce();
  });
});
