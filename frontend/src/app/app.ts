import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgentService } from './agent.service';
import { Board } from './board';
import { marked } from 'marked';

interface Message { role: 'user' | 'agent'; text: string; tools?: string[]; }

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, Board],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private agent = inject(AgentService);

  fen = signal('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
  question = '';
  messages = signal<Message[]>([]); 
  loading = signal(false);

  send(): void {
    const q = this.question.trim();
    if (!q || this.loading()) return;

    this.messages.update((m) => [...m, { role: 'user', text: q }]);
    this.question = '';
    this.loading.set(true);

    this.agent.ask(q, this.fen()).subscribe({ 
      next: (res) => {
        this.messages.update((m) => [...m, {
          role: 'agent',
          text: res.answer,
          tools: res.tools_used.map((t) => t.tool),
        }]);
        this.loading.set(false);
      },
      error: (err) => {
        this.messages.update((m) => [...m, { role: 'agent', text: 'Erreur : ' + (err.message ?? '') }]);
        this.loading.set(false);
      },
    });
  }

  onBoardFen(fen: string): void {
    this.fen.set(fen);          // le plateau met à jour la position analysée
  }

  render(md: string): string {
    return marked.parse(md) as string;   // Markdown → HTML
  }
}