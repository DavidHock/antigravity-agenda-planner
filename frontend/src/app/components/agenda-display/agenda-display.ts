import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { ApiService } from '../../services/api';

interface AgendaItem {
  time_slot?: string;
  title: string;
  description: string;
  duration?: string;
  type?: string;
}

interface AgendaDay {
  date: string;
  start_time: string;
  end_time: string;
  items: AgendaItem[];
}

interface AgendaData {
  title: string;
  summary: string;
  items?: AgendaItem[];
  days?: AgendaDay[];
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
    return lowerTitle.includes('break') || lowerTitle.includes('lunch') || lowerTitle.includes('coffee') || lowerTitle.includes('pause') || lowerTitle.includes('dinner') || lowerTitle.includes('social') || lowerTitle.includes('abendessen') || lowerTitle.includes('sozial');
  }

  getIconForTitle(title: string): string {
    const lower = title.toLowerCase();
    if (lower.includes('coffee') || lower.includes('kaffee')) return '☕';
    if (lower.includes('lunch') || lower.includes('mittag')) return '🍽️';
    if (lower.includes('dinner') || lower.includes('social') || lower.includes('abendessen') || lower.includes('sozial')) return '🍻';
    if (lower.includes('break') || lower.includes('pause')) return '🧘';
    if (lower.includes('intro')) return '👋';
    if (lower.includes('conclu') || lower.includes('wrap')) return '🏁';
    return '📅';
  }

  copyToClipboard() {
    navigator.clipboard.writeText(this.agendaContent);
  }

  downloadIcs() {
    // Build URL with query parameters
    const params = new URLSearchParams({
      topic: this.topic,
      start_time: this.startTime,
      end_time: this.endTime,
      location: this.location,
      agenda_content: this.agendaContent
    });

    // Open URL directly - browser should trigger calendar app
    window.open(`http://localhost:8086/create-ics?${params.toString()}`, '_blank');
  }

  downloadDayIcs(dayIndex: number) {
    if (!this.parsedAgenda || !this.parsedAgenda.days) return;

    const day = this.parsedAgenda.days[dayIndex];
    // Create a temporary agenda object for this day
    const dayAgenda = {
      title: `${this.parsedAgenda.title} - Day ${dayIndex + 1}`,
      summary: this.parsedAgenda.summary,
      items: day.items
    };

    const params = new URLSearchParams({
      topic: `${this.topic} (Day ${dayIndex + 1})`,
      start_time: `${day.date}T${day.start_time}:00`,
      end_time: `${day.date}T${day.end_time}:00`,
      location: this.location,
      agenda_content: JSON.stringify(dayAgenda)
    });

    window.open(`http://localhost:8086/create-ics?${params.toString()}`, '_blank');
  }
}
