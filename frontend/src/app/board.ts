import { Component, signal, output } from '@angular/core';
import { NgxChessgroundComponent } from 'ngx-chessground';
import { Chessground } from 'chessground';
import type { Api } from 'chessground/api';
import type { Key } from 'chessground/types';
import { Chess, SQUARES } from 'chess.js';

@Component({
  selector: 'app-board',
  standalone: true,
  imports: [NgxChessgroundComponent],
  template: `<ngx-chessground [runFunction]="runFn()" />`,
  styles: [`
    :host { display: block; width: 400px; height: 400px; }
    ::ng-deep cg-board,
    ::ng-deep .cg-wrap { width: 400px; height: 400px; }
  `],
})
export class Board {
  fenChange = output<string>();           // émet le FEN complet à chaque coup

  private chess = new Chess();
  private api: Api | null = null;

  runFn = signal<(el: HTMLElement) => Api>((el) => {
    const api = Chessground(el, {
      fen: this.chess.fen(),
      orientation: 'white',
      movable: {
        free: false,                      // pas de coups libres : chess.js arbitre
        color: 'white',
        dests: this.legalDests(),         // coups légaux calculés par chess.js
        events: { after: (o, d) => this.onMove(o, d) },
      },
    });
    this.api = api;
    return api;
  });

  private legalDests(): Map<Key, Key[]> {
    const dests = new Map<Key, Key[]>();
    for (const sq of SQUARES) {
      const moves = this.chess.moves({ square: sq, verbose: true });
      if (moves.length) dests.set(sq as Key, moves.map((m) => m.to as Key));
    }
    return dests;
  }

  private onMove(orig: Key, dest: Key): void {
    this.chess.move({ from: orig, to: dest, promotion: 'q' });   // promotion en dame par défaut
    const turn = this.chess.turn() === 'w' ? 'white' : 'black';
    this.api?.set({
      fen: this.chess.fen(),
      turnColor: turn,
      movable: { color: turn, dests: this.legalDests() },
    });
    this.fenChange.emit(this.chess.fen());   // FEN complet → parent
  }

  reset(): void {
    this.chess.reset();
    this.api?.set({
      fen: this.chess.fen(),
      turnColor: 'white',
      movable: { color: 'white', dests: this.legalDests() },
    });
    this.fenChange.emit(this.chess.fen());   // remet aussi le FEN du chat à la position initiale
  }
}