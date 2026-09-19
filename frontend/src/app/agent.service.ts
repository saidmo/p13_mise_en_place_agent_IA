import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AgentResponse {
  answer: string;
  tools_used: { tool: string; args: any }[];
}

@Injectable({ providedIn: 'root' })
export class AgentService {
  
  private readonly apiUrl =`${window.location.protocol}//${window.location.hostname}:9000/api/v1/agent/chat`;

  constructor(private http: HttpClient) {}

  ask(question: string, fen: string): Observable<AgentResponse> {
    return this.http.post<AgentResponse>(this.apiUrl, { question, fen });
  }
}