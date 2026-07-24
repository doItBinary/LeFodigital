import { TestBed } from '@angular/core/testing';
import { FormGroup } from '@angular/forms';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { GamificationService } from '../../core/services/gamification.service';
import { BlogService } from './blog.service';
import { BlogComponent } from './blog.component';

describe('BlogComponent', () => {
  it('creates posts and comments and refreshes progress', async () => {
    const list = vi.fn().mockReturnValue(of([]));
    const create = vi.fn().mockReturnValue(of({}));
    const comment = vi.fn().mockReturnValue(of({}));
    const loadProgress = vi.fn().mockReturnValue(of({}));
    await TestBed.configureTestingModule({
      imports: [BlogComponent],
      providers: [
        { provide: BlogService, useValue: { list, create, comment } },
        { provide: GamificationService, useValue: { load: loadProgress } },
      ],
    }).compileComponents();
    const component = TestBed.createComponent(BlogComponent)
      .componentInstance as unknown as {
      form: FormGroup;
      comments: Record<string, string>;
      ngOnInit(): void;
      create(): void;
      comment(postId: string): void;
    };
    component.ngOnInit();
    component.form.setValue({ title: 'Aprendizaje', content: 'Contenido educativo' });
    component.create();
    component.comments['post-1'] = 'Buen aporte';
    component.comment('post-1');
    expect(create).toHaveBeenCalledWith('Aprendizaje', 'Contenido educativo');
    expect(comment).toHaveBeenCalledWith('post-1', 'Buen aporte');
    expect(loadProgress).toHaveBeenCalledOnce();
  });
});
