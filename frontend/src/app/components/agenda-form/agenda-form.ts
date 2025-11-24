import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { ApiService } from '../../services/api';
import { AgendaDisplayComponent } from '../agenda-display/agenda-display';

@Component({
  selector: 'app-agenda-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressBarModule,
    MatDatepickerModule,
    MatNativeDateModule,
    AgendaDisplayComponent
  ],
  templateUrl: './agenda-form.html',
  styleUrls: ['./agenda-form.scss']
})
export class AgendaFormComponent {
  agendaForm: FormGroup;
  selectedFiles: File[] = [];
  isLoading = false;
  generatedAgenda: string | null = null;

  constructor(private fb: FormBuilder, private apiService: ApiService) {
    const now = new Date();
    const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);

    this.agendaForm = this.fb.group({
      topic: ['', Validators.required],
      startDate: [now, Validators.required],
      startTime: [this.formatTime(now), Validators.required],
      endDate: [now, Validators.required],
      endTime: [this.formatTime(oneHourLater), Validators.required],
      emailContent: ['']
    });
  }

  private formatTime(date: Date): string {
    return date.toTimeString().substring(0, 5);
  }

  onFileSelected(event: any) {
    if (event.target.files) {
      for (let i = 0; i < event.target.files.length; i++) {
        this.selectedFiles.push(event.target.files[i]);
      }
    }
  }

  removeFile(index: number) {
    this.selectedFiles.splice(index, 1);
  }

  onSubmit() {
    if (this.agendaForm.valid) {
      this.isLoading = true;
      this.generatedAgenda = null;

      const formValue = this.agendaForm.value;

      // Combine Date and Time
      const startDateTime = this.combineDateAndTime(formValue.startDate, formValue.startTime);
      const endDateTime = this.combineDateAndTime(formValue.endDate, formValue.endTime);

      this.apiService.generateAgenda(
        formValue.topic,
        this.toLocalISOString(startDateTime),
        this.toLocalISOString(endDateTime),
        formValue.emailContent,
        this.selectedFiles
      ).subscribe({
        next: (response) => {
          this.generatedAgenda = response.agenda;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error generating agenda:', error);
          this.isLoading = false;
        }
      });
    }
  }

  private combineDateAndTime(date: Date, time: string): Date {
    const [hours, minutes] = time.split(':').map(Number);
    const newDate = new Date(date);
    newDate.setHours(hours);
    newDate.setMinutes(minutes);
    newDate.setSeconds(0);
    newDate.setMilliseconds(0);
    return newDate;
  }

  private toLocalISOString(date: Date): string {
    const offset = date.getTimezoneOffset() * 60000; // offset in milliseconds
    const localISOTime = (new Date(date.getTime() - offset)).toISOString().slice(0, -1);
    return localISOTime;
  }
}
