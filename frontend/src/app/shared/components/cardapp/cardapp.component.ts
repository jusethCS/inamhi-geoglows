import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-cardapp',
  standalone: true,
  imports: [],
  templateUrl: './cardapp.component.html',
  styleUrl: './cardapp.component.css'
})
export class CardappComponent {
  @Input() imageUrl: string | undefined;
  @Input() appName: string | undefined;

}
