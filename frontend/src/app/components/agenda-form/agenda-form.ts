import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
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
    this.agendaForm = this.fb.group({
      topic: ['', Validators.required],
      duration: ['60 minutes', Validators.required],
      emailContent: ['']
    });
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
      const { topic, duration, emailContent } = this.agendaForm.value;

      this.apiService.generateAgenda(topic, duration, emailContent, this.selectedFiles).subscribe({
        next: (response) => {
          this.generatedAgenda = response.agenda;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error generating agenda:', error);
          this.isLoading = false;
          // Handle error (show snackbar etc.)
        }
      });
    }
  }
}
