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

import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-agenda-display',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatListModule, MatDividerModule, MatInputModule, FormsModule],
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

  dayEditableContent: string[] = [];

  constructor(private apiService: ApiService) { }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['agendaContent'] && this.agendaContent) {
      try {
        this.parsedAgenda = JSON.parse(this.agendaContent);
        this.rawContent = '';
        this.initializeEditableContent();
      } catch (e) {
        console.warn('Could not parse agenda as JSON, falling back to raw text');
        this.parsedAgenda = null;
        this.rawContent = this.agendaContent;
        this.dayEditableContent = [];
      }
    }
  }

  initializeEditableContent() {
    if (!this.parsedAgenda) return;

    this.dayEditableContent = [];

    if (this.parsedAgenda.days) {
      this.parsedAgenda.days.forEach(day => {
        this.dayEditableContent.push(this.formatItemsToText(day.items));
      });
    } else if (this.parsedAgenda.items) {
      // Single day / simple list
      this.dayEditableContent.push(this.formatItemsToText(this.parsedAgenda.items));
    }
  }

  formatItemsToText(items: AgendaItem[]): string {
    const textParts: string[] = [];

    items.forEach(item => {
      const icon = this.getIconForTitle(item.title);
      const formattedTitle = `${icon} ${item.title.toUpperCase()}`;

      if (item.time_slot) {
        let header = `${item.time_slot} - ${formattedTitle}`;
        if (item.duration) {
          const cleanDuration = item.duration.replace(' mins', '').replace(' min', '');
          header += ` (${cleanDuration} min)`;
        }
        textParts.push(header);
      } else {
        textParts.push(`* ${formattedTitle}`);
      }

      if (item.description) {
        let shortDesc = item.description.split('.')[0] + '.';
        if (shortDesc.length > 100) {
          shortDesc = shortDesc.substring(0, 97) + '...';
        }
        textParts.push(`  ${shortDesc}`);
      }
      textParts.push('');
    });

    return textParts.join('\n');
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
    if (!this.parsedAgenda) {
      navigator.clipboard.writeText(this.agendaContent);
      return;
    }

    const textParts: string[] = [];
    textParts.push((this.parsedAgenda.title || 'Meeting Agenda').toUpperCase());
    textParts.push('='.repeat(textParts[0].length));
    textParts.push('');

    if (this.parsedAgenda.summary) {
      textParts.push(this.parsedAgenda.summary);
      textParts.push('');
    }

    const processItems = (items: AgendaItem[]) => {
      items.forEach(item => {
        const icon = this.getIconForTitle(item.title);
        const formattedTitle = `${icon} ${item.title.toUpperCase()}`;

        if (item.time_slot) {
          let header = `${item.time_slot} - ${formattedTitle}`;
          if (item.duration) {
            const cleanDuration = item.duration.replace(' mins', '').replace(' min', '');
            header += ` (${cleanDuration} min)`;
          }
          textParts.push(header);
        } else {
          textParts.push(`* ${formattedTitle}`);
        }

        if (item.description) {
          let shortDesc = item.description.split('.')[0] + '.';
          if (shortDesc.length > 100) {
            shortDesc = shortDesc.substring(0, 97) + '...';
          }
          textParts.push(`  ${shortDesc}`);
        }
        textParts.push('');
      });
    };

    if (this.parsedAgenda.days) {
      this.parsedAgenda.days.forEach((day, index) => {
        textParts.push(`DAY ${index + 1} - ${day.date}`);
        textParts.push('-'.repeat(40));
        processItems(day.items);
        textParts.push('');
      });
    } else if (this.parsedAgenda.items) {
      textParts.push('AGENDA ITEMS:');
      textParts.push('-'.repeat(40));
      textParts.push('');
      processItems(this.parsedAgenda.items);
    }

    navigator.clipboard.writeText(textParts.join('\n'));
  }

  downloadIcs() {
    // Build URL with query parameters
    const params = new URLSearchParams({
      topic: this.topic,
      start_time: this.startTime,
      end_time: this.endTime,
      location: this.location,
      agenda_content: this.agendaContent // Keep original for now, or we need to reconstruct the JSON from text which is hard. 
      // Actually, for "Download All", we might want to keep the JSON structure but update descriptions? 
      // The user asked: "download ics buttons should include the edits of the description".
      // Since we are moving to text boxes, maybe we should just send the text content if possible?
      // But the backend expects JSON for structure. 
      // Let's stick to the per-day download for the edited text feature as requested "next to each download button".
      // For "Download All", it's tricky if we have multiple text blocks.
      // Let's assume the user primarily wants the per-day text edits.
      // Wait, the user said "instead of showing a layouted webview directly show the ICS style description text... Allow editing these boxes and the download ics buttons should include the edits".
      // This implies the "Download All" should also include edits. 
      // Reconstructing JSON from text is error prone.
      // However, the backend `create_ics` endpoint falls back to raw text if JSON parsing fails.
      // So for single day, we can send the text.
      // For multi-day, we can't easily send multiple text blocks as one "agenda_content" string unless we concatenate them.
      // Let's try to update the JSON object with the new text? No, parsing text back to JSON items is hard.
      // Let's construct a "Plain Text" agenda for the backend to use directly.
    });

    // For now, let's implement the per-day download correctly first, as that maps 1:1 to the text box.
    // We will update this method to use the edited content if it's a single day.

    let contentToSend = this.agendaContent;
    if (this.dayEditableContent.length === 1) {
      contentToSend = this.dayEditableContent[0];
    } else if (this.dayEditableContent.length > 1) {
      // Concatenate all days
      contentToSend = this.dayEditableContent.join('\n\n' + '='.repeat(20) + '\n\n');
    }

    const params2 = new URLSearchParams({
      topic: this.topic,
      start_time: this.startTime,
      end_time: this.endTime,
      location: this.location,
      agenda_content: contentToSend
    });

    // Open URL directly - browser should trigger calendar app
    window.open(`http://localhost:8086/create-ics?${params2.toString()}`, '_blank');
  }

  downloadDayIcs(dayIndex: number) {
    if (!this.parsedAgenda || !this.parsedAgenda.days) return;

    const day = this.parsedAgenda.days[dayIndex];
    const editedText = this.dayEditableContent[dayIndex];

    const params = new URLSearchParams({
      topic: `${this.topic} (Day ${dayIndex + 1})`,
      start_time: `${day.date}T${day.start_time}:00`,
      end_time: `${day.date}T${day.end_time}:00`,
      location: this.location,
      agenda_content: editedText // Send the edited text directly
    });

    window.open(`http://localhost:8086/create-ics?${params.toString()}`, '_blank');
  }

  refineDay(index: number) {
    const currentText = this.dayEditableContent[index];
    if (!currentText) return;

    // Show loading state if possible (skipping for now to keep it simple)
    this.apiService.refineText(currentText).subscribe({
      next: (response) => {
        if (response.refined_text) {
          this.dayEditableContent[index] = response.refined_text;
        }
      },
      error: (err) => {
        console.error('Error refining text:', err);
        alert('Failed to refine text. Please try again.');
      }
    });
  }
}
