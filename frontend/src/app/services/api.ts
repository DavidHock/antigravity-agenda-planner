import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8086';

  constructor(private http: HttpClient) { }

  generateAgenda(topic: string, duration: string, emailContent: string, files: File[]): Observable<any> {
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('duration', duration);
    if (emailContent) {
      formData.append('email_content', emailContent);
    }

    if (files && files.length > 0) {
      for (let file of files) {
        formData.append('files', file);
      }
    }

    return this.http.post(`${this.apiUrl}/generate-agenda`, formData);
  }
}
