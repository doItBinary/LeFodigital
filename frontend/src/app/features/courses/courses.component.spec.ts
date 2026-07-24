import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { FormGroup } from '@angular/forms';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../core/services/auth.service';
import { CoursesService } from './courses.service';
import { CoursesComponent } from './courses.component';

describe('CoursesComponent', () => {
  it('loads courses and lets a teacher create one', async () => {
    const list = vi.fn().mockReturnValue(of([]));
    const create = vi.fn().mockReturnValue(of({}));
    await TestBed.configureTestingModule({
      imports: [CoursesComponent],
      providers: [
        { provide: CoursesService, useValue: { list, create } },
        { provide: AuthService, useValue: { isTeacher: signal(true) } },
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { queryParamMap: convertToParamMap({ create: '1' }) } },
        },
      ],
    }).compileComponents();
    const component = TestBed.createComponent(CoursesComponent)
      .componentInstance as unknown as {
      form: FormGroup;
      showCreate(): boolean;
      ngOnInit(): void;
      create(): void;
    };
    component.ngOnInit();
    expect(component.showCreate()).toBe(true);
    component.form.setValue({ name: 'Curso rural', description: 'Descripción' });
    component.create();
    expect(create).toHaveBeenCalledWith('Curso rural', 'Descripción');
    expect(list).toHaveBeenCalledTimes(2);
  });
});
