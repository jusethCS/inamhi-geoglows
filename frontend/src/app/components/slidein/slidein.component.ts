import { Component, OnInit, ElementRef } from '@angular/core';
import { trigger, state, style, animate, transition } from '@angular/animations';

@Component({
  selector: 'slidein',
  standalone: true,
  imports: [],
  templateUrl: './slidein.component.html',
  styleUrl: './slidein.component.css',
  animations: [
    trigger('slideIn', [
      state('hidden', style({
        transform: 'translateY(60%)',
        opacity: 0
      })),
      state('visible', style({
        transform: 'translateY(0)',
        opacity: 1
      })),
      transition('hidden => visible', [
        animate('1s ease-out')
      ]),
    ]),
  ]
})

export class SlideinComponent implements OnInit{
  public isVisible = 'hidden';

  constructor(private el: ElementRef) {}

  ngOnInit() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.isVisible = 'visible';
          observer.unobserve(this.el.nativeElement.querySelector('.animated-div'));
        }
      });
    }, { threshold: 0.1 });
    observer.observe(this.el.nativeElement.querySelector('.animated-div'));
  }

}
