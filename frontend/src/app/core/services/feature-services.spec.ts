import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { BlogService } from '../../features/blog/blog.service';
import { ChatService } from '../../features/chat/chat.service';
import { CoursesService } from '../../features/courses/courses.service';
import { ReportsService } from '../../features/reports/reports.service';
import { GamificationService } from './gamification.service';

describe('Feature API services', () => {
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('uses the course endpoints', () => {
    const service = TestBed.inject(CoursesService);
    service.list().subscribe();
    http.expectOne('/api/v1/courses').flush([]);
    service.create('Curso', 'Descripción').subscribe();
    const request = http.expectOne('/api/v1/courses');
    expect(request.request.method).toBe('POST');
    expect(request.request.body.name).toBe('Curso');
  });

  it('uses blog and report endpoints', () => {
    const blog = TestBed.inject(BlogService);
    blog.list().subscribe();
    http.expectOne('/api/v1/posts').flush([]);
    blog.create('Título', 'Contenido').subscribe();
    http.expectOne('/api/v1/posts').flush({});
    blog.comment('post-1', 'Comentario').subscribe();
    http.expectOne('/api/v1/posts/post-1/comments').flush({});

    const reports = TestBed.inject(ReportsService);
    reports.student().subscribe();
    http.expectOne('/api/v1/reports/student/me').flush({});
    reports.teacher().subscribe();
    http.expectOne('/api/v1/reports/teacher').flush({});
  });

  it('loads progress and keeps it in a signal', () => {
    const service = TestBed.inject(GamificationService);
    service.load().subscribe();
    http.expectOne('/api/v1/gamification/me').flush({
      points: 50,
      level: 1,
      completedActivities: 1,
      medals: [],
      pointsInLevel: 50,
    });
    expect(service.progress()?.points).toBe(50);
  });

  it('sends only the ten most recent chat messages', () => {
    const service = TestBed.inject(ChatService);
    const messages = Array.from({ length: 12 }, (_, index) => ({
      role: 'user' as const,
      content: `Mensaje ${index}`,
    }));
    service.send(messages).subscribe();
    const request = http.expectOne('/api/v1/chat/messages');
    expect(request.request.body.messages).toHaveLength(10);
  });
});
