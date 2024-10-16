import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';

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
  @Input() appUrl: string | undefined;
  @Input() hRef: string | undefined;

  constructor(private router: Router) {}

  public redirigir(): void {
    if(this.hRef){
      window.location.href = this.hRef;
    }
    if(this.appUrl){
      this.router.navigate([this.appUrl]);
    }
  }

}
