import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { ApiService } from '../../services/api';

interface AgendaItem {
  time_slot: string;
  title: string;
  description: string;
  duration: string;
}

interface AgendaData {
  title: string;
  summary: string;
  items: AgendaItem[];
}

@Component({
  selector: 'app-agenda-display',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatListModule, MatDividerModule],
  templateUrl: './agenda-display.html',
  styleUrls: ['./agenda-display.scss']
})
export class AgendaDisplayComponent implements OnChanges {
  @Input() agendaContent: string = '';
  @Input() topic: string = '';
  @Input() location: string = '';
  @Input() startTime: string = '';
  @Input() endTime: string = '';

  parsedAgenda: AgendaData | null = null;
  rawContent: string = '';

  constructor(private apiService: ApiService) { }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['agendaContent'] && this.agendaContent) {
      try {
        this.parsedAgenda = JSON.parse(this.agendaContent);
        this.rawContent = '';
      } catch (e) {
        console.warn('Could not parse agenda as JSON, falling back to raw text');
        this.parsedAgenda = null;
        this.rawContent = this.agendaContent;
      }
    }
  }

  isBreakItem(title: string): boolean {
    const lowerTitle = title.toLowerCase();
    return lowerTitle.includes('break') || lowerTitle.includes('lunch') || lowerTitle.includes('coffee');
  }

  getIconForTitle(title: string): string {
    const lower = title.toLowerCase();
    if (lower.includes('coffee')) return '☕';
    if (lower.includes('lunch')) return '🍱';
    if (lower.includes('break')) return '🧘';
    if (lower.includes('intro')) return '👋';
    if (lower.includes('conclu') || lower.includes('wrap')) return '🏁';
    return '📅';
  }

  copyToClipboard() {
    navigator.clipboard.writeText(this.agendaContent);
  }

  downloadIcs() {
    // Use an iframe to submit the form without navigating away
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.name = 'download_iframe';
    document.body.appendChild(iframe);

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'http://localhost:8086/create-ics';
    form.target = 'download_iframe';

    // Add form fields
    const fields = {
      topic: this.topic,
      start_time: this.startTime,
      end_time: this.endTime,
      location: this.location,
      agenda_content: this.agendaContent
    };

    for (const [key, value] of Object.entries(fields)) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = value;
      form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();

    // Cleanup after a delay
    setTimeout(() => {
      document.body.removeChild(form);
      document.body.removeChild(iframe);
    }, 1000);
  }
}
