import { RouterOutlet } from '@angular/router';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { HeaderComponent } from '../../shared/header/header.component';
import { SlideinComponent } from '../../shared/slidein/slidein.component';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faCircleInfo } from '@fortawesome/free-solid-svg-icons';
import { faGithub } from '@fortawesome/free-brands-svg-icons';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    RouterOutlet,
    MatButtonModule,
    HeaderComponent,
    FontAwesomeModule,
    SlideinComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})

export class HomeComponent {

  infoIcon = faCircleInfo;
  infoGitHub = faGithub;

  @ViewChild('about') myScrollContainer!: ElementRef;
  scrollToElement(): void {
    const element = this.myScrollContainer.nativeElement;
    element.scrollIntoView({ behavior: 'auto', block: 'start' });
  }



}
