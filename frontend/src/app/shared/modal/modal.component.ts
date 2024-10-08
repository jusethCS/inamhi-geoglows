import { Component, ElementRef, ViewChild } from '@angular/core';
import { Modal } from 'bootstrap';

@Component({
  selector: 'app-modal',
  standalone: true,
  imports: [],
  templateUrl: './modal.component.html',
  styleUrl: './modal.component.css'
})
export class ModalComponent {
  @ViewChild('panelModal') exampleModal: ElementRef | undefined;

  openModal() {
    if(this.exampleModal){
      const modal = new Modal(this.exampleModal.nativeElement);
      modal.show();
    }
  }

}
