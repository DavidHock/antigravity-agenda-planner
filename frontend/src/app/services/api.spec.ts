import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

import { ApiService } from './api';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('sends form data when generating an agenda', () => {
    service.generateAgenda('Topic', '2024-05-01T10:00:00', '2024-05-01T11:00:00', 'DE', '', [])
      .subscribe();

    const req = httpMock.expectOne('http://localhost:8086/generate-agenda');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toBeInstanceOf(FormData);
    req.flush({ agenda: '{}' });
  });

  it('sends ICS creation requests as blobs', () => {
    service.createIcs('Topic', 'start', 'end', 'Room', '{}').subscribe(blob => {
      expect(blob).toBeTruthy();
    });

    const req = httpMock.expectOne('http://localhost:8086/create-ics');
    expect(req.request.responseType).toBe('blob');
    req.flush(new Blob());
  });
});
