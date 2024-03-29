import { RouterOutlet } from '@angular/router';
import { Component, ViewChild, ElementRef } from '@angular/core';
import {MatButtonModule} from '@angular/material/button';
import { HeaderComponent } from '../../shared/components/header/header.component';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterOutlet, MatButtonModule, HeaderComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})

export class HomeComponent {

  @ViewChild('second') myScrollContainer!: ElementRef;

  scrollToElement(): void {
    const element = this.myScrollContainer.nativeElement;
    element.scrollIntoView({ behavior: 'auto', block: 'start' });
  }
}
