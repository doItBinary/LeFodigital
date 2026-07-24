import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ActivitiesService } from './activities.service';

describe('ActivitiesService', () => {
  let service: ActivitiesService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ActivitiesService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('covers the activity lifecycle endpoints', () => {
    service.list().subscribe();
    expect(http.expectOne('/api/v1/activities').request.method).toBe('GET');

    service
      .create({
        title: 'Actividad',
        description: '',
        points: 10,
        dueDate: null,
        courseId: null,
      })
      .subscribe();
    expect(http.expectOne('/api/v1/activities').request.method).toBe('POST');

    service.publish('activity-1').subscribe();
    expect(http.expectOne('/api/v1/activities/activity-1/publish').request.method).toBe('POST');

    service.complete('activity-1').subscribe();
    expect(http.expectOne('/api/v1/activities/activity-1/complete').request.method).toBe('POST');

    service.remove('activity-1').subscribe();
    expect(http.expectOne('/api/v1/activities/activity-1').request.method).toBe('DELETE');
  });

  it('uploads, lists and downloads authorized evidence', () => {
    service.upload('activity-1', new File(['test'], 'evidence.pdf')).subscribe();
    const upload = http.expectOne('/api/v1/activities/activity-1/evidence');
    expect(upload.request.body instanceof FormData).toBe(true);

    service.evidences('activity-1').subscribe();
    expect(http.expectOne('/api/v1/activities/activity-1/evidences').request.method).toBe('GET');

    service.download('evidence-1').subscribe();
    const download = http.expectOne('/api/v1/evidences/evidence-1/download');
    expect(download.request.responseType).toBe('blob');
  });
});
