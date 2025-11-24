import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8086';

  constructor(private http: HttpClient) { }

  generateAgenda(topic: string, startTime: string, endTime: string, emailContent: string, files: File[]): Observable<any> {
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('start_time', startTime);
    formData.append('end_time', endTime);
    if (emailContent) {
      formData.append('email_content', emailContent);
    }

    files.forEach(file => {
      formData.append('files', file);
    });

    return this.http.post<any>(`${this.apiUrl}/generate-agenda`, formData);
  }

  createIcs(topic: string, startTime: string, endTime: string, location: string, agendaContent: string): Observable<Blob> {
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('start_time', startTime);
    formData.append('end_time', endTime);
    formData.append('location', location);
    formData.append('agenda_content', agendaContent);

    return this.http.post(`${this.apiUrl}/create-ics`, formData, { responseType: 'blob' });
  }
}
